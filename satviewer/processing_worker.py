import const
from aws.aws_helpers import upload_to_s3
from aws.sqs import send_image_done, QUEUE_NAME_REQUESTED, get_sqs_queue, JobMessage, get_sqs

from satviewer.processing import ImageCalculator


def check_new_jobs(visibility_timeout=300,
                wait_time_seconds=20):

    q = get_sqs_queue(queue_name=QUEUE_NAME_REQUESTED)
    sqs = get_sqs()
    while True:
        jobs = q.receive_messages(VisibilityTimeout=visibility_timeout,
                              WaitTimeSeconds=wait_time_seconds, MaxNumberOfMessages=1, MessageAttributeNames=['All'])
        if jobs:
            job = JobMessage.from_message(jobs[0])
            print("Received message " + job.img_uri)
            sqs.delete_message(QueueUrl=q.url, ReceiptHandle=jobs[0].receipt_handle)
            print("Message deleted")
            process_job(job)
            print("Processing finished")

def process_job(job: JobMessage):
    calculator = ImageCalculator.for_job(job)
    calculator.get_files()
    filepath = calculator.save_result()
    upload_to_s3(bucket_name=const.OUTPUT_BUCKET, key=job.key, filepath=filepath)
    message_id = send_image_done(job)
    print("Message image-done sent: {}".format(message_id))
    print("Image {} processed".format(job.img_uri))


if __name__ == "__main__":
    check_new_jobs()