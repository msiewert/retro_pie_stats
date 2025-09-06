from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class LambdaResources:
    def __init__(self, scope: Construct, dynamo_table):
        # Lambda function for API
        self.get_stats_fn = _lambda.Function(
            scope,
            "GetStatsFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="get_stats.lambda_handler",
            code=_lambda.Code.from_asset("retro_pie_stats/lambda"),
            environment={"TABLE_NAME": dynamo_table.table_name},
        )
        dynamo_table.grant_read_data(self.get_stats_fn)

        # Lambda Function URL
        self.fn_url = self.get_stats_fn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )
