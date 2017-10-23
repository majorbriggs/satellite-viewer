import requests
from requests.auth import HTTPBasicAuth
import os

from const import WORKSPACE, GEOSERVER_USERNAME, GEOSERVER_PASSWORD, DATA_ROOT, GEOSERVER_URL

GEOSERVER_REST_URL = GEOSERVER_URL + "rest/"

auth = HTTPBasicAuth(username=GEOSERVER_USERNAME, password=GEOSERVER_PASSWORD)



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

def delete_store(ws, cs):
    headers = {'Content-Type': 'text/xml'}
    url = GEOSERVER_REST_URL + 'workspaces/{ws}/coveragestores/{cs}'.format(ws=ws, cs=cs)
    try:
        r = requests.delete(url=url, headers=headers,
                          auth=auth, params={'recurse':"true"})
        check_response(r)

    except requests.ConnectionError:
        print("Connection to Geoserver failed on creation of Layer.")

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


def add_stores_for_datasets(datasets, data_root=DATA_ROOT):

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

def add_layers_for_datasets(datasets):
    suffixes = ['RGB', 'NDVI', 'TEMP']
    for dataset in datasets:
        image_id = dataset.split('__')[-1]
        for suffix in suffixes:
            image_filename = "{image_id}_{suffix}.tif".format(image_id=image_id,
                                                              suffix=suffix)
            cs_name = "{}_{}".format(image_id, suffix)
            add_layer(ws=WORKSPACE, cs=cs_name, name=cs_name, title=cs_name)

def delete_stores_for_dataset(image_id):
    suffixes = ['RGB', 'NDVI', 'TEMP']
    for suffix in suffixes:
        cs_name = "{}_{}".format(image_id, suffix)
        delete_store(ws=WORKSPACE, cs=cs_name)

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
    pass