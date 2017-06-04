from aws.sqs import get_sqs_queue, QUEUE_NAME_DONE, send_image_on_geoserver
from geoserver.geoserver_api import add_new_image

def check_new_jobs(visibility_timeout=300,
                wait_time_seconds=20):

    q = get_sqs_queue(queue_name=QUEUE_NAME_DONE)
    while True:
        jobs = q.receive_messages(VisibilityTimeout=visibility_timeout,
                              WaitTimeSeconds=wait_time_seconds, MaxNumberOfMessages=1)
        if jobs:
            process_job(img_uri=jobs[0].body)


def process_job(img_uri):
    img_id = img_uri.replace('/', '')
    add_new_image(img_id)
    send_image_on_geoserver(img_id)

if __name__ == "__main__":
    check_new_jobs()