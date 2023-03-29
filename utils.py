import boto3
import json
import os
from botocore.config import Config

config = Config(retries={"max_attempts": 10, "mode": "standard"})

STS = boto3.client("sts")

AWS_REGION = os.environ["AWS_REGION"]


def get_account_id():
    """Return current account Id"""

    account_info = STS.get_caller_identity()

    return account_info["Account"]


def get_accounts():
    """Get all AWS Accounts"""
    try:
        if get_account_id() != "122611646899":
            CROSS_ACCOUNT_ROLE_ARN = (
                "arn:aws:iam::122611646899:role/cp-security-hub-notification-role"
            )
            credentials = STS.assume_role(
                RoleArn=CROSS_ACCOUNT_ROLE_ARN, RoleSessionName="aws-sec-notifications"
            )
            boto3_session = boto3.Session(
                aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
                aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
                aws_session_token=credentials["Credentials"]["SessionToken"],
            )

            org = boto3_session.client("organizations", config=config)
            paginator = org.get_paginator("list_accounts")
            accounts = {}
            for page in paginator.paginate():
                for account in page["Accounts"]:
                    if account["Status"] == "ACTIVE":
                        accounts[account["Id"]] = account

            return accounts
        else:
            org = boto3.client("organizations", config=config)
            paginator = org.get_paginator("list_accounts")
            accounts = {}
            for page in paginator.paginate():
                for account in page["Accounts"]:
                    if account["Status"] == "ACTIVE":
                        accounts[account["Id"]] = account

            return accounts
    except Exception as e:
        raise e


ACCOUNT_ID = get_account_id()
ACCOUNTS = get_accounts()


def send_message(SNS, message):
    """Send SNS Message"""

    client = boto3.client("sns")
    response = client.publish(
        TopicArn=SNS,
        Message=json.dumps({"default": (json.dumps(message))}),
        MessageStructure="json",
    )
