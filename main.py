import json
import os
import threading
from loguru import logger

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

stop_flag = False

def process_message():
    global stop_flag
    while not stop_flag:
        try:
            #Set sqs client
            sqs = boto3.client('sqs', region_name=AWS_REGION, aws_access_key_id=ACCESS_KEY ,
                           aws_secret_access_key=SECRET_ACCESS_KEY)

            #Receieve message
            response = sqs.receive_message(
                QueueUrl=P1_QUEUE,
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            messages = response.get('Messages')

            #If there are messages in queue
            if messages is not None:
                #Get the first message
                message = messages[0]
                logger.info(f"Message received from queue with ID: {message["MessageId"]}")

                #Get the body
                body = json.loads(message['Body'])

                #Validate the body
                if "title" in body and "description" in body:
                    if body["title"] and body["description"]:

                        #Create teams card
                        payload = {
                            "@type": "MessageCard",
                            "@context": "http://schema.org/extensions",
                            "themeColor": "FF0000",
                            "title": body["title"],
                            "text": body["description"]
                        }
                        teams_message = pymsteams.connectorcard(TEAMS_WEBHOOK)
                        teams_message.payload = payload

                        #Send teams card
                        logger.info("Sending Teams alert")
                        teams_message.send()
                        logger.info(f"Teams alert sent, payload: {json.dumps(payload)}")

                    #Display error messages if anything is missing on the body
                    else:
                        logger.error("Either the title or description or both are empty")
                else:
                    logger.error("Either the title or description or both are missing from the SQS message")

                #Delete message from queue
                sqs.delete_message(
                    QueueUrl=P1_QUEUE,
                    ReceiptHandle=message['ReceiptHandle']
                )
                logger.info(f"Message deleted from queue with ID: {message["MessageId"]}")

            #If there are no messages log that
            else:
                logger.info("No messages in queue")

        except Exception as e:
            logger.error(f"An error occurred: {e}")

def background_thread():
    thread = threading.Thread(target=process_message, daemon=True)
    thread.start()
    return thread

bg_thread = background_thread()

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0")
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        stop_flag = True
        bg_thread.join()

@app.route('/', methods=['GET'])
def health_check():
    return 'OK', 200