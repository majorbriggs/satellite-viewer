import os
import shutil

from django.core.exceptions import ImproperlyConfigured

import const
from aws.aws_helpers import download_landsat_bands, download_mtl_json, get_landsat_image_id_from_s3_key, get_s2_image_id_from_s3_key, download_sentinel_bands
from raster_processing import calculate_rgb, calculate_ndvi, calculate_ts, calculate_landsat_toa_reflectance
from geoserver.geoserver_api import add_coverage_store, add_layer, add_style_to_layer
from const import WORKSPACE, NDVI, RGB, TEMP, LANDSAT, SENTINEL
DATA_ROOT = const.GEOSERVER_STORAGE.split('file://')[-1]

def add_to_database(s3_key, src_dir, source=LANDSAT):
    try:
        from viewer.models import add_image
        from raster_processing import get_image_info

        i = get_image_info(key=s3_key, src_dir=src_dir, source=source)
        add_image(i)
    except ImproperlyConfigured as e:
        print("Not running from Django - cannot add to database")

def add_geoserver_layers(output_dir, image_id, layers=None):
    if layers is None:
        layers = (NDVI, RGB, TEMP)
    for layer_type in layers:
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
    if "landsat" in s3_key:
        add_landsat_image_set(s3_key)
    elif "tiles" in s3_key:
        add_s2_image_set(s3_key)

def add_s2_image_set(s3_key):
    bands = [2, 3, 4, 8]
    image_id = get_s2_image_id_from_s3_key(s3_key)
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
    download_sentinel_bands(dir_uri=s3_key, bands=bands, output_dir=sources_dirpath)
    calculate_rgb(sources_dirpath, os.path.join(output_dirpath, "{}_RGB.tif".format(image_id)),
                  with_cloud_mask=False, source=SENTINEL)
    calculate_ndvi(sources_dirpath, os.path.join(output_dirpath, "{}_NDVI.tif".format(image_id)),
                   with_cloud_mask=True, source=SENTINEL)
    add_geoserver_layers(output_dirpath, image_id, layers=(RGB, NDVI))
    add_to_database(s3_key, src_dir=sources_dirpath, source=SENTINEL)
    delete_source_files(sources_dirpath)

def add_landsat_image_set(s3_key):
    bands = [2, 3, 4, 5, 10, 'QA']
    image_id = get_landsat_image_id_from_s3_key(s3_key)
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
    is_pre_collection = not image_id.startswith('LC0')
    download_landsat_bands(dir_uri=s3_key, bands=bands, output_dir=sources_dirpath)
    download_mtl_json(dir_uri=s3_key, output_dir=sources_dirpath)
    calculate_rgb(sources_dirpath, os.path.join(output_dirpath, "{}_RGB.tif".format(image_id)), with_cloud_mask=True,
                  is_pre_collection=is_pre_collection)
    calculate_ts(sources_dirpath, os.path.join(output_dirpath, "{}_TEMP.tif".format(image_id)), with_cloud_mask=False,
                 is_pre_collection=is_pre_collection)

    calculate_landsat_toa_reflectance(sources_dirpath)
    calculate_ndvi(sources_dirpath, os.path.join(output_dirpath, "{}_NDVI.tif".format(image_id)), with_cloud_mask=False,
                   is_pre_collection=is_pre_collection)
    add_geoserver_layers(output_dirpath, image_id)
    add_to_database(s3_key, src_dir=sources_dirpath)
    delete_source_files(sources_dirpath)

def delete_image_files(image_id):
    images_dirpath = os.path.join(DATA_ROOT, image_id)
    delete_source_files(images_dirpath)

if __name__ == "__main__":
    img = "s3://landsat-pds/c1/L8/190/022/LC08_L1TP_190022_20170528_20170615_01_T1/"
    s2_key = 'tiles/34/U/CF/2017/5/28/0/'
    path = 'sentinel-s2-l1c.s3-website.eu-central-1.amazonaws.com/#tiles/10/S/DG/2015/12/7/0/'
    add_landsat_image_set(img)