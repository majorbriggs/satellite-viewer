import logging

import boto3
from botocore.errorfactory import ClientError

logger = logging.getLogger(__name__)

REGION_NAME = 'eu-central-1'
QUEUE_NAME_REQUESTED = 'img-requested-queue'
QUEUE_NAME_DONE = 'img-done-queue'
QUEUE_NAME_ON_GEOSERVER = 'img-on-geoserver-queue'

class JobMessage:

    def __init__(self, source, img_uri, process):
        self.source = source
        self.img_uri = img_uri
        self.process = process
        self.key = "{img_id}_{process}.tiff".format(img_id=img_uri.replace('/', ''), process=process)


    def get_message_attributes(self):
        return {"key": {"DataType":"String", "StringValue": self.key},
                "source":{"DataType":"String", "StringValue":self.source},
                "img_uri":{"DataType":"String","StringValue":self.img_uri},
                "process":{"DataType":"String","StringValue":self.process}}

    @classmethod
    def from_message(cls, message):
        attrs = message.message_attributes
        source=attrs['source']['StringValue']
        process = attrs['process']['StringValue']
        img_uri = attrs['img_uri']['StringValue']
        return cls(source=source, process=process, img_uri=img_uri)

def get_sqs(region_name=REGION_NAME):
    sqs = boto3.client('sqs', region_name=region_name)
    return sqs

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


def send_image_requested(job: JobMessage):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_REQUESTED, region_name=REGION_NAME)
    return send_message(queue=queue, message_content="Image Dupa",
                        message_attributes=job.get_message_attributes())


def send_image_done(job: JobMessage):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_DONE, region_name=REGION_NAME)
    return send_message(queue=queue, message_content="Image processed",
                        message_attributes=job.get_message_attributes())


def send_image_on_geoserver(job: JobMessage):
    queue = get_sqs_queue(queue_name=QUEUE_NAME_ON_GEOSERVER, region_name=REGION_NAME)
    return send_message(queue=queue, message_content="Image on Geoserver",
                        message_attributes=job.get_message_attributes())

