import requests
from requests.auth import HTTPBasicAuth
import os

import const
from const import WORKSPACE, GEOSERVER_REST_URL
from aws.sqs import JobMessage


auth = HTTPBasicAuth(username=os.getenv('GEOSERVER_USERNAME'), password=os.getenv('GEOSERVER_PASSWORD'))


def check_response(r):
    if r.status_code == 201:
        return True
    else:
        print('Request failed\n{} {}'.format(r.status_code, r.content))
        return False


def create_workspace(name):
    headers = {'Content-Type': 'text/xml'}

    url = GEOSERVER_REST_URL + 'workspaces'

    try:
        r = requests.post(url=url, headers=headers,
                          auth=auth, data='<workspace><name>{}</name></workspace>'.format(name))
        check_response(r)
    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Workspace")


def add_coverage_store(ws, cs, path):
    headers = {'Content-Type': 'application/xml'}

    url = GEOSERVER_REST_URL + 'workspaces/{ws}/coveragestores'.format(ws=ws)
    try:
        r = requests.post(url=url, headers=headers,
                          auth=auth,
                          data='<coverageStore><name>{cs}</name><workspace>{ws}</workspace><type>GeoTIFF</type><url>{'
                               'path}</url><enabled>true</enabled></coverageStore> '
                          .format(cs=cs, ws=ws, path=path))
        check_response(r)
    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Coverage Store")


def add_layer(ws, cs, name, title):
    headers = {'Content-Type': 'text/xml'}
    data = "<coverage><name>{name}</name><nativeName>{name}</nativeName><title>{title}</title></coverage>"
    data = data.format(cs=cs, name=name, title=title)
    url = GEOSERVER_REST_URL + 'workspaces/{ws}/coveragestores/{cs}/coverages'.format(ws=ws, cs=cs)
    try:
        r = requests.post(url=url, headers=headers,
                          auth=auth, data=data)
        check_response(r)
    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Layer.")


def add_new_image(job: JobMessage):
    img_id = job.key.replace(".tiff", '')
    add_coverage_store(WORKSPACE, img_id, path='{storage}/{key}'.format(storage=const.GEOSERVER_STORAGE, key=job.key))
    add_layer(ws=WORKSPACE, cs=img_id, name=img_id, title=img_id)


if __name__ == "__main__":
    pass
