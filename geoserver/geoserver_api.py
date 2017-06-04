import requests
from requests.auth import HTTPBasicAuth
import os

GEOSERVER_REST_URL = 'http://ec2-52-57-36-143.eu-central-1.compute.amazonaws.com:8080/geoserver/rest/'
WORKSPACE = "sat-viewer"


headers = {'Content-Type': 'text/xml'}
auth = HTTPBasicAuth(username=os.getenv('GEOSERVER_USERNAME'), password=os.getenv('GEOSERVER_PASSWORD'))

def check_response(r):
    if r.status_code == 201:
        return True
    else:
        print('Request failed\n{} {}'.format(r.status_code, r.content))
        return False

def create_workspace(name):
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
                      auth=auth, data='<coverageStore><name>{cs}</name><workspace>{ws}</workspace><type>GeoTIFF</type><url>{path}</url><enabled>true</enabled></coverageStore>'
                          .format(cs=cs, ws=ws, path=path))
        check_response(r)
    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Coverage Store")

def add_layer(ws, cs, name, title):
    headers = {'Content-Type': 'text/xml'}
    data = "<coverage><name>{name}</name><nativeName>{name}</nativeName><title>{title}</title></coverage>".format(cs=cs, name=name, title=title )
    url = GEOSERVER_REST_URL + 'workspaces/{ws}/coveragestores/{cs}/coverages'.format(ws=ws, cs=cs)
    try:
        r = requests.post(url=url, headers=headers,
                  auth=auth, data=data)
        check_response(r)
    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Layer.")


def add_new_image(img_id):
    add_coverage_store(WORKSPACE, img_id, path = 'file:///home/ubuntu/{img_id}'.format(img_id=img_id))
    add_layer(ws=WORKSPACE, cs=img_id, name=img_id, title=img_id)


if __name__ == "__main__":
    pass