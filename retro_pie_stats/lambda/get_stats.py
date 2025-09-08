import json
import os

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    limit = int(params.get("limit", 10))
    last_key = params.get("last_key")

    scan_kwargs = {"Limit": limit}
    if last_key:
        scan_kwargs["ExclusiveStartKey"] = json.loads(last_key)

    response = table.scan(**scan_kwargs)
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "items": response.get("Items", []),
                "last_key": (
                    json.dumps(response.get("LastEvaluatedKey"))
                    if response.get("LastEvaluatedKey")
                    else None
                ),
            }
        ),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    }
