import requests
from requests.auth import HTTPBasicAuth
import os

import const
from const import WORKSPACE
from aws.sqs import JobMessage

GEOSERVER_REST_URL = "http://localhost:8080/geoserver/" + "rest/"
auth = HTTPBasicAuth(username=os.getenv('GEOSERVER_USERNAME'), password=os.getenv('GEOSERVER_PASSWORD'))

DATASETS = ['2015_04_21__LC81900222015111LGN00',
                '2017_04_10__LC81900222017100LGN00',
                '2017_05_12__LC81900222017132LGN00',
                '2017_05_28__LC81900222017148LGN00']

DATA_ROOT = '/home/piotrek/mgr/datasets/'


def check_response(r):
    if r.status_code == 201:
        return True
    else:
        print('Request failed\n{} {}'.format(r.status_code, r.text))
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


def add_new_image_from_job_message(job: JobMessage):
    img_id = job.key.replace(".tiff", '')
    add_coverage_store(WORKSPACE, img_id, path='{storage}{key}'.format(storage=const.GEOSERVER_STORAGE, key=job.key))
    add_layer(ws=WORKSPACE, cs=img_id, name=img_id, title=img_id)


def add_style(name, sld):
    headers = {"Content-Type": "application/vnd.ogc.sld+xml"}
    params = {"name": name}
    url = GEOSERVER_REST_URL + "styles"
    r = requests.post(url=url, headers=headers,
                      auth=auth,
                      params=params,
                      data=sld)
    if r.status_code == 201:
        print("Style added successfully")
    else:
        raise ValueError("Adding style failed with response: {} \n{}".format(r.status_code, r.text))


def add_stores_for_datasets(datasets=DATASETS, data_root=DATA_ROOT):

    suffixes = ['RGB', 'NDVI', 'TEMP']
    for dataset in datasets:
        image_id = dataset.split('__')[-1]
        for suffix in suffixes:
            image_filename = "{image_id}_{suffix}.tif".format(image_id=image_id,
                                                              suffix=suffix)
            image_path = os.path.join(data_root, dataset, image_filename)
            cs_name = "{}_{}".format(image_id, suffix)

            add_coverage_store(WORKSPACE,
                               cs=cs_name,
                               path=image_path)

def add_layers_for_datasets(datasets=DATASETS):
    suffixes = ['RGB', 'NDVI', 'TEMP']
    for dataset in datasets:
        image_id = dataset.split('__')[-1]
        for suffix in suffixes:
            image_filename = "{image_id}_{suffix}.tif".format(image_id=image_id,
                                                              suffix=suffix)
            cs_name = "{}_{}".format(image_id, suffix)
            add_layer(ws=WORKSPACE, cs=cs_name, name=cs_name, title=cs_name)


def get_all_layers_names():
    headers = {'Content-Type': 'text/json'}
    url = GEOSERVER_REST_URL + 'layers.json'

    r = requests.get(url=url, headers=headers,
                      auth=auth)

    response_dict = r.json()
    return [layer["name"] for layer in response_dict["layers"]["layer"]]

def add_style_to_layer(layer, style, ws = WORKSPACE):
    headers = {'Content-Type': 'text/xml'}

    url = GEOSERVER_REST_URL + "layers/{}:{}".format(ws, layer)
    data = "<layer><defaultStyle><name>{}</name></defaultStyle></layer>".format(style)
    r = requests.put(url=url, headers=headers,
                      auth=auth, data=data)

    if r.status_code != 200:
        print(r.text)
    else:
        print("Style {} added to layer {}".format(style, layer))

if __name__ == "__main__":
    for layer in get_all_layers_names():
        if layer.endswith("NDVI"):
            add_style_to_layer(layer, "ndvi")
        elif layer.endswith("TEMP"):
            add_style_to_layer(layer, "temperature")
