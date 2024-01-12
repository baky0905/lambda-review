import json
import os
import random
import string

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from constants import REGION
from utils.config import LOGGER
from utils.metadata import get_nationality

REQUIRED_KEYS = [
    'first_name',
    'event_name',
    'ticket_count',
]

DYNAMODB_CLIENT = boto3.client('dynamodb', region_name=REGION)


def _generate_response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message}),
        'headers': {'Content-Type': 'application/json'},
    }


def _load_json_body(event):
    try:
        body = json.loads(event['body'])
        return body
    except json.JSONDecodeError as e:
        return _generate_response(400, 'Invalid JSON format: ' + str(e))
    except KeyError as e:
        return _generate_response(400, f'Missing key: {e}')
    except Exception as e:
        return _generate_response(500, 'Unexpected error: ' + str(e))


def _generate_random_string(length):
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def handler(event, _):
    LOGGER.info(f'Event: {event}.')
    if 'body' not in event:
        return _generate_response(400, 'Missing request body.')

    body = _load_json_body(event)
    LOGGER.info(f'Body: {event}.')

    missing_keys = [key for key in REQUIRED_KEYS if key not in body.keys() or not body[key]]
    if missing_keys:
        missing_keys_str = ', '.join(missing_keys)
        LOGGER.error(f'Invalid request, required key(s) are missing: {missing_keys_str}.')
        return _generate_response(
            status_code=400,
            message=f'Invalid request, required key(s) are missing: {missing_keys_str}.',
        )

    event_name = body['event_name']
    first_name = body['first_name']
    try:
        ticket_count = int(body['ticket_count'])
    except ValueError:
        LOGGER.exception(f'ticket_count must be an integer. Received: {body.get("ticket_count")}')
        return _generate_response(400, 'Invalid ticket_count: must be an integer.')

    item = {
        'ticket_id': {'S': _generate_random_string(5)},
        'event_name': {'S': event_name},
        'first_name': {'S': first_name},
        'nationality': {'S': get_nationality(first_name)},
        'ticket_count': {'N': str(ticket_count)}
    }

    try:
        table_name = os.getenv('TABLE_NAME')
        LOGGER.info(f'Attempting to insert item: {item} into table: {table_name}')
        DYNAMODB_CLIENT.put_item(TableName=table_name, Item=item)

        return _generate_response(
            status_code=200,
            message=f'Successfully booked {ticket_count} tickets for event:{event_name} by person: {first_name}.',
        )

    except (BotoCoreError, ClientError) as e:
        LOGGER.exception('Error inserting item into DynamoDB.')
        return _generate_response(500, 'Internal server error.')

