import logging

import boto3
from botocore.errorfactory import ClientError

logger = logging.getLogger(__name__)

REGION_NAME = 'eu-central-1'
QUEUE_NAME = 'img-queue'

def get_sqs_queue(queue_name, region_name=REGION_NAME):
    sqs = boto3.resource('sqs', region_name=region_name)
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except ClientError as e:
        if e.__class__.__name__ == "QueueDoesNotExist":
            logger.info("Queue '{}' did not exist")
            queue = sqs.create_queue(QueueName=queue_name)
        else:
            raise e
    return queue

def send_message(message_content, queue_name=QUEUE_NAME, reqion_name=REGION_NAME, message_attributes={}):
    queue = get_sqs_queue(queue_name=queue_name, region_name=reqion_name)
    return queue.send_message(MessageBody=message_content, MessageAttributes=message_attributes)


