import json
import os

from ticket_sum import handler


def test_sum_tickets_with_data(dynamodb_client, create_dynamodb_mock_table):
    items = [
        {
            'ticket_id': str(i),
            'first_name': 'first_name' + str(i),
            'event_name': 'event_name' + str(i),
            'nationality': 'nationality' + str(i),
            'ticket_count': str(i),
        }
        for i in range(5)
    ]

    for item in items:
        dynamodb_client.put_item(
            TableName=os.getenv('TABLE_NAME'),
            Item={
                'ticket_id': {'S': item['ticket_id']},
                'first_name': {'S': item['first_name']},
                'event_name': {'S': item['event_name']},
                'nationality': {'S': item['nationality']},
                'ticket_count': {'N': item['ticket_count']},
            },
        )

    expected_code = 200
    expected_message = 'Total tickets booked: 10.'

    response = handler({}, {})

    assert response['statusCode'] == expected_code
    assert json.loads(response['body'])['message'] == expected_message


def test_sum_tickets_no_data(create_dynamodb_mock_table):

    expected_code = 200
    expected_message = 'Total tickets booked: 0.'

    response = handler({}, {})

    assert response['statusCode'] == expected_code
    assert json.loads(response['body'])['message'] == expected_message
