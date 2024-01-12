import json
import os

import boto3
from constants import REGION


def handler(event, context):
    dynamodb_client = boto3.client('dynamodb', region_name=REGION)
    table_name = os.getenv('TABLE_NAME')

    try:
        response = dynamodb_client.scan(
            TableName=table_name,
            AttributesToGet=[
                "ticket_count",
            ]
        )
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error."}),
        }

    items = response["Items"]
    total_ticket_count = sum(int(item['ticket_count']['N']) for item in items)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Total tickets booked: {total_ticket_count}."}),
    }
