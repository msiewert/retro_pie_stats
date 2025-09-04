from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

class DynamoResources:
    def __init__(self, scope: Construct):
        self.table = dynamodb.Table(
            scope, "RetroPieStatsTable",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )