import logging
import os

import boto3
import moto
import pytest


# How do I avoid tests from mutating my real infrastructure
# https://docs.getmoto.org/en/latest/docs/getting_started.html#how-do-i-avoid-tests-from-mutating-my-real-infrastructure
@pytest.fixture(scope='session', autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


@pytest.fixture
def dynamodb_client():
    dynamodb_client = boto3.client('dynamodb', region_name=os.getenv('REGION'))

    yield dynamodb_client


@pytest.fixture
def create_dynamodb_mock_table(dynamodb_client, monkeypatch):
    with moto.mock_dynamodb():
        monkeypatch.setenv('TABLE_NAME', 'test-table')

        dynamodb_client.create_table(
            TableName=os.getenv('TABLE_NAME'),
            KeySchema=[{'AttributeName': 'event_name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'event_name', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
        )

        yield

        # The teardown (cleanup) is implicit.
        # Moto will automatically discard the mock environment here.
        # i.e. no need for dynamodb_client.delete_table(TableName=os.getenv('TABLE_NAME'))
