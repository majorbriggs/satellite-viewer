from aws.sqs import send_image_done, QUEUE_NAME_REQUESTED, get_sqs_queue


def check_new_jobs(visibility_timeout=300,
                wait_time_seconds=20):

    q = get_sqs_queue(queue_name=QUEUE_NAME_REQUESTED)
    while True:
        jobs = q.receive_messages(VisibilityTimeout=visibility_timeout,
                              WaitTimeSeconds=wait_time_seconds, MaxNumberOfMessages=1)
        if jobs:
            process_job(img_uri=jobs[0].body)

def process_job(img_uri):
    send_image_done(img_bucket_uri=img_uri)
    print("Image {} done".format(img_uri))


def download_tci():
    pass

def upload_to_s3():
    pass


if __name__ == "__main__":
    check_new_jobs()