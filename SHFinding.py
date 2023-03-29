import string
from utils import ACCOUNTS


class SHFinding(object):
    def __init__(self, event) -> None:
        self.Severity = event["Severity"]["Label"]
        self.Title = event["Title"]
        self.WorkflowStatus = event["Workflow"]["Status"]
        self.RecordState = event["RecordState"]
        self.Region = event["Region"]
        self.Company = event["CompanyName"]
        self.Product = event["ProductName"]
        self.AWSAccountId = event["AwsAccountId"]
        self.AWSAccount = self.set_account()

    def set_account(self):
        return ACCOUNTS[self.AWSAccountId]["Name"]


class Access_Analyzer_Finding(object):
    def __init__(self, event) -> None:
        self.Id = event["id"]
        self.ResourceType = event["resourceType"]
        self.Status = event["status"]
        self.Resource = event["resource"]
        self.IsPublic = event["isPublic"]
        self.Action = event["action"]
        self.Condition = event["condition"]
        self.Principal = event["principal"]
        self.CreatedAtTime = event["createdAt"]
        self.UpdateAtTime = event["updatedAt"]
        self.ResourceOwnerId = event["resourceOwnerAccount"]
        self.ResourceOwnerName = self.set_account()
        self.Type = self.set_finding_type()

    def set_finding_type(self):
        if (
            self.ResourceType == "AWS::IAM::Role"
            and self.Action == ["sts:AssumeRole"]
            and list(self.Principal.keys())[0] == "AWS"
        ):
            return "EXTERNAL_ACCOUNT_TRUST"

    def set_account(self):
        return ACCOUNTS[self.ResourceOwnerId]["Name"]
