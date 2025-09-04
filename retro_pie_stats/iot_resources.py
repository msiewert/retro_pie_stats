from aws_cdk import aws_iot as iot
from aws_cdk import aws_iam as iam
from constructs import Construct

class IotResources:
    def __init__(self, scope: Construct, dynamo_table, certificate_arn: str):
        # IAM role for IoT to access DynamoDB
        self.role = iam.Role(
            scope, "IotToDynamoRole",
            assumed_by=iam.ServicePrincipal("iot.amazonaws.com"),
        )
        self.role.add_to_policy(iam.PolicyStatement(
            actions=["dynamodb:PutItem"],
            resources=[dynamo_table.table_arn]
        ))

        # IoT Topic Rule
        self.rule = iot.CfnTopicRule(
            scope, "GameStatsRule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'game/stats'",
                actions=[
                    iot.CfnTopicRule.ActionProperty(                        
                        dynamo_d_bv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                            put_item=iot.CfnTopicRule.PutItemInputProperty(
                                table_name=dynamo_table.table_name
                            ),
                            role_arn=self.role.role_arn
                        )
                    )
                ],
                rule_disabled=False
            )
        )

        # IoT Thing
        self.thing = iot.CfnThing(
            scope, "RetroPieStatsThing",
            thing_name="RetroPieStatsThing"
        )

        # Attach existing certificate to thing
        self.thing_principal_attachment = iot.CfnThingPrincipalAttachment(
            scope, "RetroPieStatsThingCertAttachment",
            thing_name=self.thing.thing_name,
            principal=certificate_arn
        )
        self.thing_principal_attachment.add_dependency(self.thing)

        # IoT Policy (restrict to connect as 'retropie' and publish to game/stats)
        self.policy = iot.CfnPolicy(
            scope, "RetroPieStatsPolicy",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Connect"
                        ],
                        "Resource": f"arn:aws:iot:{scope.region}:{scope.account}:client/retropie"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Publish"
                        ],
                        "Resource": f"arn:aws:iot:{scope.region}:{scope.account}:topic/game/stats"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Subscribe"
                        ],
                        "Resource": f"arn:aws:iot:{scope.region}:{scope.account}:topicfilter/game/stats"
                    }
                ]
            },
            policy_name="RetroPieStatsPolicy"
        )

        # Attach policy to certificate
        self.policy_principal_attachment = iot.CfnPolicyPrincipalAttachment(
            scope, "RetroPieStatsPolicyCertAttachment",
            policy_name=self.policy.policy_name,
            principal=certificate_arn
        )
        self.policy_principal_attachment.add_dependency(self.policy)