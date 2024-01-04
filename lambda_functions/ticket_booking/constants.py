import os

REGION = os.getenv('REGION', os.getenv('AWS_DEFAULT_REGION', 'eu-west-1'))
