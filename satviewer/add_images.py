import os
import shutil

from django.core.exceptions import ImproperlyConfigured

import const
from aws.aws_helpers import download_landsat_bands, download_mtl_json, get_image_id_from_s3_key, Image
from raster_processing import calculate_rgb, calculate_ndvi, calculate_ts
from geoserver.geoserver_api import add_coverage_store, add_layer, add_style_to_layer
from const import WORKSPACE, NDVI, RGB, TEMP
DATA_ROOT = const.GEOSERVER_STORAGE.split('file://')[-1]

def add_to_database(s3_key, src_dir):
    try:
        from viewer.models import add_image
        from raster_processing import get_landsat_image_info

        i = get_landsat_image_info(key=s3_key, src_dir=src_dir)
        add_image(i)
    except ImproperlyConfigured as e:
        print("Not running from Django - cannot add to database")

def add_geoserver_layers(output_dir, image_id):
    for layer_type in (NDVI, RGB, TEMP):
        geoserver_layer_name = "{}_{}".format(image_id, layer_type)
        filename = "{}_{}.tif".format(image_id, layer_type)
        filepath = os.path.join(output_dir, filename)
        add_coverage_store(ws=WORKSPACE, cs=geoserver_layer_name, path=filepath)
        add_layer(ws=WORKSPACE, cs=geoserver_layer_name, name=geoserver_layer_name,
                  title=geoserver_layer_name)
        add_style_to_layer(geoserver_layer_name, style=layer_type)


def delete_source_files(sources_dirpath):
    try:
        shutil.rmtree(sources_dirpath)
        print(sources_dirpath + ' deleted')
    except FileNotFoundError:
        pass

def add_image_set(s3_key):
    bands = [2, 3, 4, 5, 10, 'QA']
    image_id = get_image_id_from_s3_key(s3_key)
    output_dirpath = os.path.join(DATA_ROOT, image_id)
    sources_dirpath = os.path.join(output_dirpath, "sources")

    try:
        os.mkdir(output_dirpath)
    except FileExistsError:
        pass
    try:
        os.mkdir(sources_dirpath)
    except FileExistsError:
        pass

    download_landsat_bands(dir_uri=s3_key, bands=bands, output_dir=sources_dirpath)
    download_mtl_json(dir_uri=s3_key, output_dir=sources_dirpath)
    calculate_ts(sources_dirpath, os.path.join(output_dirpath, "{}_TEMP.tif".format(image_id)), with_cloud_mask=True)
    calculate_rgb(sources_dirpath, os.path.join(output_dirpath, "{}_RGB.tif".format(image_id)), with_cloud_mask=True)
    calculate_ndvi(sources_dirpath, os.path.join(output_dirpath, "{}_NDVI.tif".format(image_id)), with_cloud_mask=True)
    add_geoserver_layers(output_dirpath, image_id)
    add_to_database(s3_key, src_dir=sources_dirpath)
    delete_source_files(sources_dirpath)

if __name__ == "__main__":
    img = "c1/L8/190/022/LC08_L1TP_190022_20170816_20170825_01_T1/"
    add_image_set(img)