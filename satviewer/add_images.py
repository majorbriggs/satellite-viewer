import os
from datetime import datetime
import rasterio

from aws.aws_helpers import download_landsat_bands, download_mtl_json
from raster_processing import calculate_rgb, calculate_ndvi, calculate_ts, band_filename

DATA_ROOT = '/home/piotrek/temp'


def add_geoserver_layers(image_id):
    pass


def add_image_set(image_id):
    bands = [2, 3, 4, 5, 10, 'QA']
    # temp_dir = "temp_{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))
    # temp_path = os.path.join(DATA_ROOT, temp_dir)
    # os.mkdir(temp_path)
    temp_path = "/home/piotrek/temp/temp_20170827174443"
    # download_landsat_bands(dir_uri=image_id, bands=bands, output_dir=temp_path)
    # download_mtl_json(image_id, output_dir=temp_path)
    # calculate_ts(temp_path, temp_path+"/TEMP.tif", with_cloud_mask=True)
    # calculate_rgb(temp_path, temp_path+"/RGB.tif", with_cloud_mask=True)
    # calculate_ndvi(temp_path, temp_path+"/NDVI.tif", with_cloud_mask=True)

    add_geoserver_layers(image_id)

if __name__ == "__main__":
    img = "c1/L8/190/022/LC08_L1TP_190022_20170816_20170825_01_T1/"
    add_image_set(image_id=img)
