import json
import os
import threading
import logging

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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_message():
    sqs = boto3.client('sqs', region_name=AWS_REGION, aws_access_key_id=ACCESS_KEY ,
                       aws_secret_access_key=SECRET_ACCESS_KEY)

    response = sqs.receive_message(
        QueueUrl=P1_QUEUE,
        MessageAttributeNames=['All'],
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )

    messages = response.get('Messages')
    if messages is not None:
        message = messages[0]
        logger.info("Message received from queue with ID" + json.dumps(response.get('MessageId')))
        body = json.loads(message['Body'])
        if "title" in body and "description" in body:
            if body["title"] and body["description"]:
                payload = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "FF0000",
                    "title": body["title"],
                    "text": body["description"]
                }

                teams_message = pymsteams.connectorcard(TEAMS_WEBHOOK)
                teams_message.payload = payload
                logger.info("Sending Teams alert")
                teams_message.send()
                logger.info("Teams alert sent, payload" + json.dumps(payload))
            else:
                logger.error("Either the title or description or both are empty")
        else:
            logger.error("Either the title or description or both are missing from the SQS message")

        sqs.delete_message(
            QueueUrl=P1_QUEUE,
            ReceiptHandle=message['ReceiptHandle']
        )
        logger.info("Message deleted from queue with ID:" + json.dumps(response.get('MessageId')))
    else:
        logger.info("No messages in queue")

if __name__ == '__main__':
    threading.Thread(target=process_message, daemon=True).start()
    app.run()

@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200