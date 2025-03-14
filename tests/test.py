import json
from unittest.mock import patch

import main

class FakeConnectorCard:
    payload = {}
    def send(self):
        return "Sent"

def set_environment_variables(queue_url):
    main.P1_QUEUE = queue_url
    main.AWS_REGION = 'eu-west-2'
    main.ACCESS_KEY = 'testing'
    main.SECRET_ACCESS_KEY = 'testing'
    main.TEAMS_WEBHOOK = 'testing'
    main.run_mode = 'test'

@patch('pymsteams.connectorcard')
def test_process_message(connectorcard_mock, sqs_client):
    print("Starting test")
    queue = sqs_client.create_queue(QueueName='queue')

    queue_url = queue['QueueUrl']

    set_environment_variables(queue_url)

    connectorcard_mock.return_value = FakeConnectorCard()

    expected_msg = json.dumps({'description': 'Happening right now', 'title': 'Bug'})

    sqs_messages = sqs_client.send_message(QueueUrl=queue_url, MessageBody=expected_msg)

    main.process_message()

    messages = sqs_messages.get('Messages')
    assert connectorcard_mock.called
    assert messages is None

@patch('pymsteams.connectorcard')
def test_process_message_wrong_data(connectorcard_mock, sqs_client):
    queue = sqs_client.create_queue(QueueName='queue')

    queue_url = queue['QueueUrl']

    set_environment_variables(queue_url)

    connectorcard_mock.return_value = FakeConnectorCard()

    expected_msg = json.dumps({'description': 'Happening right now'})

    sqs_messages = sqs_client.send_message(QueueUrl=queue_url, MessageBody=expected_msg)

    main.process_message()

    messages = sqs_messages.get('Messages')

    assert connectorcard_mock.called == False
    assert messages is None