import json
import os
import boto3
import logging

from botocore.exceptions import ClientError
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from base64 import b64decode
from utils import send_message, ACCOUNT_ID, AWS_REGION
from SHFinding import Access_Analyzer_Finding

AA_NAME = os.environ["ANALYZER_NAME"]
SNS = os.getenv("SNS_TOPIC")
SLACK_CHANNEL = os.environ["slackChannel"]


AA_CLIENT = boto3.client("accessanalyzer")


logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def get_analyzer_arn():
    """Return Access Analyzer Arn in the region"""

    return f"arn:aws:access-analyzer:{AWS_REGION}:{ACCOUNT_ID}:analyzer/{AA_NAME}-{AWS_REGION}"


def get_secret(channel):
    SECRET_NAME = os.environ["webhook_secret"]
    region_name = "ap-southeast-2"
    secret = ""

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as e:
        print(f"error occurred: {e}")
        exit(1)
    if "SecretString" in get_secret_value_response:
        secret = get_secret_value_response["SecretString"]

    # print("exiting function")

    return json.loads(secret)[channel]


def prepare_message(check):
    subject = "IAM Access Analyzer - Finding - External AWS Account Trusted by IAM Role"
    if check.Type == "EXTERNAL_ACCOUNT_TRUST":
        external_account = check.Principal["AWS"]
    message = f"""\n
        {subject}: \n
        AWS Account Name: {check.ResourceOwnerName}\n
        Resource: {check.Resource}\n
        Trusted Account: {external_account}\n
        Time: {check.UpdateAtTime}\n
        Finding Type: {check.Type}\n
        Finding Status: {check.Status}\n
       """

    return message


def send_slack_message(message, secret):
    HOOK_URL = "https://" + secret
    slack_message = {"channel": SLACK_CHANNEL, "text": message}
    req = Request(HOOK_URL, json.dumps(slack_message).encode("utf-8"))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message["channel"])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


def get_aa_findings():
    results = []

    paginator = AA_CLIENT.get_paginator("list_findings")
    response_iterator = paginator.paginate(
        analyzerArn=get_analyzer_arn(), filter={"status": {"eq": ["ACTIVE"]}}
    )

    for page in response_iterator:
        if "findings" in page:
            results += page["findings"]

    return results


def lambda_handler(event, context):
    source_event = json.dumps(event)
    channel = "Test"
    secret = get_secret(channel)

    if "schedule" in source_event:
        print(f"Scheduled run...")
        finding_types = {"ROLE": "AWS::IAM::Role"}
        role_findings = get_aa_findings()
        if role_findings:
            for finding in role_findings:
                if finding["resourceType"] == finding_types["ROLE"]:
                    check = Access_Analyzer_Finding(finding)
                    if check.Type == "EXTERNAL_ACCOUNT_TRUST":
                        message = prepare_message(check)
                        send_slack_message(message, secret)
