import json
import os
import logging

from utils import send_message, AWS_REGION
from SHFinding import SHFinding


SNS = os.getenv("SNS_TOPIC")
ACCOUNT_ID = os.environ["SNS_TOPIC_ACCOUNT_ID"]

logger = logging.getLogger()


def _setting_console_logging_level():
    """
    Determines whether or not debug logging should be enabled based on the env var.
    Defaults to false.
    """
    if os.getenv("DEBUG_ENABLED", "false").lower() == "true":
        print("enabling debug mode")
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def is_suppressed_check(product, title):
    skip_list = {
        "Systems Manager Patch Manager": ["All"],
        "Inspector": ["All"],
        "Prowler": ["All"],
        "Security Hub": ["KMS.3 AWS KMS keys should not be deleted unintentionally"],
    }
    if product in list(skip_list.keys()):
        if skip_list[product] == ["All"] or title in skip_list[product]:
            return True
        else:
            return False


def lambda_handler(event, context):
    _setting_console_logging_level()
    sns_topic = f"arn:aws:sns:{AWS_REGION}:{ACCOUNT_ID}:{SNS}"
    for finding in event["detail"]["findings"]:
        logger.info("Finding")
        logger.info(json.dumps(finding))

        # print(json.dumps(finding['Title']))
        if finding["ProductName"] == "IAM Access Analyzer":
            print(finding["Title"])
        skip_alert = is_suppressed_check(finding["ProductName"], finding["Title"])
        if skip_alert:
            print(
                f'Skipping notification: {finding["ProductName"]} - {finding["Title"]}'
            )
        else:
            check = SHFinding(finding)
            finding["AwsAccountId"] = check.AWSAccount
            message = event
            message["detail"]["findings"] = [finding]
            send_message(sns_topic, message)
