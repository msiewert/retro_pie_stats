from aws_cdk import (
    Stack,
)
from constructs import Construct

from .dynamo_resources import DynamoResources
from .iot_resources import IotResources
from .lambda_resources import LambdaResources

class RetroPieStatsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, certificate_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.dynamo = DynamoResources(self)
        self.iot = IotResources(self, self.dynamo.table, certificate_arn)
        self.lambda_resources = LambdaResources(self, self.dynamo.table)