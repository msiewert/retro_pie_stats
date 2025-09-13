import json
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb: Any = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ["TABLE_NAME"])

# Load API key from environment variable
API_KEY = os.environ["API_KEY"]


def lambda_handler(event, _context) -> dict[str, Any]:
    # Handle CORS preflight requests (check both httpMethod and requestContext)
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get(
        "http", {}
    ).get("method")
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,x-api-key,X-Api-Key,X-API-Key",
            },
        }

    # Check API key in headers
    headers = event.get("headers", {})
    provided_key = (
        headers.get("x-api-key") or headers.get("X-API-Key") or headers.get("X-Api-Key")
    )

    if not provided_key or provided_key != API_KEY:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }

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
            "Access-Control-Allow-Headers": "Content-Type,x-api-key,X-Api-Key,X-API-Key",
        },
    }
