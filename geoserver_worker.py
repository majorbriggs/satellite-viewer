from aws.sqs import get_sqs_queue, get_sqs, QUEUE_NAME_DONE, send_image_on_geoserver, JobMessage
from aws.aws_helpers import download_from_s3
from geoserver.geoserver_api import add_new_image
from const import OUTPUT_BUCKET

def check_new_jobs(visibility_timeout=300,
                wait_time_seconds=20):

    q = get_sqs_queue(queue_name=QUEUE_NAME_DONE)
    sqs = get_sqs()
    while True:
        jobs = q.receive_messages(VisibilityTimeout=visibility_timeout,
                              WaitTimeSeconds=wait_time_seconds, MaxNumberOfMessages=1, MessageAttributeNames=['All'])
        if jobs:
            receipt_handle = jobs[0].receipt_handle
            sqs.delete_message(QueueUrl=q.url, ReceiptHandle=receipt_handle)
            print("Message deleted")
            process_job(JobMessage.from_message(jobs[0]))
            print("Processing finished")


def process_job(job: JobMessage):
    print("Received message {}".format(job.key))
    download_from_s3(bucket_name=OUTPUT_BUCKET, key=job.key, filepath=job.key)
    add_new_image(job)
    send_image_on_geoserver(job)


if __name__ == "__main__":
    check_new_jobs()