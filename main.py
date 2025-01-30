import json
import os

import boto3
import pymsteams
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)
# loading variables from .env file
load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
P1_QUEUE = os.getenv('P1_QUEUE')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
TEAMS_WEBHOOK = os.getenv('TEAMS_WEBHOOK')


def process_message():
    sqs = boto3.client('sqs', region_name=AWS_REGION, aws_access_key_id=ACCESS_KEY ,
                       aws_secret_access_key=SECRET_ACCESS_KEY)

    response = sqs.receive_message(QueueUrl=P1_QUEUE, MessageAttributeNames=['All'],
                                   MaxNumberOfMessages=1, WaitTimeSeconds=20)

    messages = response.get('Messages')
    if messages is not None:
        message = messages[0]
        body = json.loads(message['Body'])

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000",
            "title": body["title"],
            "text": body["description"]
        }

        teams_message = pymsteams.connectorcard(TEAMS_WEBHOOK)
        teams_message.payload = payload
        teams_message.send()


        sqs.delete_message(
            QueueUrl=P1_QUEUE,
            ReceiptHandle=message['ReceiptHandle']
        )
    else:
        print("No messages in queue")

if __name__ == '__main__':
    process_message()
    app.run()

@app.route('/health', methods=['GET'])
def health_check():
    return 'Service is all good', 200