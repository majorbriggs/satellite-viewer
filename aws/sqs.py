import logging

import boto3
from botocore.errorfactory import ClientError

logger = logging.getLogger(__name__)

REGION_NAME = 'eu-central-1'
QUEUE_NAME_REQUESTED = 'img-requested-queue'
QUEUE_NAME_DONE = 'img-done-queue'
QUEUE_NAME_ON_GEOSERVER = 'img-on-geoserver-queue'


def get_sqs_queue(queue_name=QUEUE_NAME_REQUESTED, region_name=REGION_NAME):
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


def send_message(message_content, queue, message_attributes=None):
    if message_attributes is None:
        message_attributes = {}
    return queue.send_message(MessageBody=message_content, MessageAttributes=message_attributes)


def send_image_requested(img_bucket_uri):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_REQUESTED, region_name=REGION_NAME)
    return send_message(queue=queue, message_content=img_bucket_uri)


def send_image_done(img_bucket_uri):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_DONE, region_name=REGION_NAME)
    return send_message(queue=queue, message_content=img_bucket_uri)


def send_image_on_geoserver(img_id):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_ON_GEOSERVER, region_name=REGION_NAME)
    return send_message(queue=queue, message_content=img_id)
