from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

from .dynamo_resources import DynamoResources
from .iot_resources import IotResources

class RetroPieStatsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, certificate_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Instantiate DynamoDB resources
        self.dynamo = DynamoResources(self)

        # IoT resources
        self.iot = IotResources(self, self.dynamo.table, certificate_arn)