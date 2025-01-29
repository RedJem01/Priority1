import json
import os

import boto3
import pymsteams
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)

def process_message():
    # loading variables from .env file
    load_dotenv()
    sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION'), aws_access_key_id=os.getenv('ACCESS_KEY'),
                       aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'))

    response = sqs.receive_message(QueueUrl=os.getenv('P3_QUEUE'), MessageAttributeNames=['All'],
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

        teams_message = pymsteams.connectorcard(os.getenv('TEAMS_WEBHOOK'))
        teams_message.payload = payload
        teams_message.send()


        sqs.delete_message(
            QueueUrl=os.getenv('P3_QUEUE'),
            ReceiptHandle=message['ReceiptHandle']
        )

if __name__ == '__main__':
    process_message()
    app.run()

@app.route('/health', methods=['GET'])
def health_check():
    return 'Service is all good', 200