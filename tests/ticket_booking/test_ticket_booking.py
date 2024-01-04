import json
import os

import pytest
import ticket_booking
import ticket_sum


@pytest.mark.parametrize(
    'input_event_body, expected_status_code, expected_message',
    [
        (
            {'ticket_count': 2},
            400,
            {
                'message': 'Invalid request, required key(s) are missing: first_name, event_name.'
            },
        ),
        (
            {'first_name': 'John', 'event_name': 'Dancing with the stars'},
            400,
            {'message': 'Invalid request, required key(s) are missing: ticket_count.'},
        ),
    ],
)
def test_handler_missing_key_return_400(
    input_event_body, expected_status_code, expected_message
):
    event = {'body': json.dumps(input_event_body)}

    response = ticket_booking.handler(event, {})

    assert response['statusCode'] == expected_status_code
    assert response['body'] == json.dumps(expected_message)


def test_handler_ticket_count_is_not_number_return_400(create_dynamodb_mock_table):
    event = {
        'body': json.dumps(
            {
                'first_name': 'John',
                'event_name': 'Dancing with the stars',
                'ticket_count': 'two',
            }
        )
    }

    response = ticket_booking.handler(event, {})

    expected_code = 400
    expected_message = json.dumps(
        {'message': 'Invalid ticket_count: must be an integer.'}
    )

    assert response['statusCode'] == expected_code
    assert response['body'] == expected_message


def test_handler_booking_written_successfully_200_returned(
    dynamodb_client, create_dynamodb_mock_table, monkeypatch
):
    event = {
        'body': json.dumps(
            {
                'first_name': 'Kristijan',
                'event_name': 'Dancing with the stars',
                'ticket_count': 2,
            }
        )
    }

    expected_code = 200
    expected_data = [
        {
            'first_name': {'S': 'Kristijan'},
            'event_name': {'S': 'Dancing with the stars'},
            'ticket_count': {'N': '2'},
            'nationality': {'S': 'MOCKED_CONTRY_CODE'},
            'ticket_id': {'S': 'DuMmYiD'},
        }
    ]

    def mock_generate_random_string(*args):
        return 'DuMmYiD'


    def mock_get_nationality(*args):
        return 'MOCKED_CONTRY_CODE'

    monkeypatch.setattr('ticket_booking._generate_random_string', mock_generate_random_string)
    monkeypatch.setattr('ticket_booking.get_nationality', mock_get_nationality)

    response = ticket_booking.handler(event, {})
    actual_data = dynamodb_client.scan(TableName=os.getenv('TABLE_NAME')).get('Items', [])

    assert response['statusCode'] == expected_code
    assert actual_data == expected_data


def test_load_json_body_valid():

    input_event = {
        "body": "{\"event_name\": \"Rammstein\", \"first_name\": \"Kristijan\", \"ticket_count\": 5}"
    }

    actual_body = ticket_booking._load_json_body(input_event)
    expected_body = {
        "event_name": "Rammstein",
        "first_name": "Kristijan",
        "ticket_count": 5
        }
    assert actual_body == expected_body


def test_load_json_body_invalid():

    input_event = {
        "body": "{event_name: \"Rammstein\", \"first_name\": \"Kristijan\", \"ticket_count\": 5}"
    }

    expected_response = ticket_booking._generate_response(400, 'Invalid JSON format: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)')
    assert ticket_booking._load_json_body(input_event) == expected_response


def test_full_happy_flow(create_dynamodb_mock_table):
    event1 = {
        'body': json.dumps(
            {
                'first_name': 'John',
                'event_name': 'Dancing with the stars',
                'ticket_count': 2,
            }
        )
    }
    event2 = {
        'body': json.dumps(
            {
                'first_name': 'Max',
                'event_name': 'Viki Cristina Barcelona',
                'ticket_count': 5,
            }
        )
    }

    book_response1 = ticket_booking.handler(event1, {})
    book_response2 = ticket_booking.handler(event2, {})

    ticket_sum_response = ticket_sum.handler({}, {})

    assert book_response1['statusCode'] == 200
    assert book_response2['statusCode'] == 200
    assert ticket_sum_response['statusCode'] == 200
    assert (
        json.loads(ticket_sum_response['body'])['message'] == 'Total tickets booked: 7.'
    )
