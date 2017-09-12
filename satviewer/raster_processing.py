from collections import namedtuple
from contextlib import contextmanager

from rio_toa import brightness_temp
import glob, os
import rasterio
import numpy as np
from l8qa.qa import cloud_confidence
from l8qa.qa_pre import cloud_qa

import json
from aws.aws_helpers import Image
Bands = namedtuple("Bands", ["R", "G", "B", "NIR", "TIRS"])

bands = Bands(R=4, G=3, B=2, NIR=5, TIRS=10)


def get_landsat_image_info(key, src_dir):
    with open(meta_filename(src_dir)) as src:
        j = json.load(src)
        clouds = j['L1_METADATA_FILE']['IMAGE_ATTRIBUTES']['CLOUD_COVER']
        date = j['L1_METADATA_FILE']['PRODUCT_METADATA']['DATE_ACQUIRED']
        key_short = key.strip('/').split('/')[-1]
        return Image(aws_bucket_uri=key_short, source="L8", data_percentage=100, clouds_percentage=clouds, date=date)

def get_cloud_mask(src_dir, is_pre_collection=False):
    with rasterio.open(band_filename(src_dir, 'QA')) as src:
        band = src.read(1)
        if is_pre_collection:
            return ~(cloud_qa(band) == 1)
        return cloud_confidence(band) == 3

def band_filename(src_dir, band_number):
    os.chdir(src_dir)
    name_pattern = "*B{}.TIF".format(band_number)
    for file in glob.glob(name_pattern):
        return file
    raise FileNotFoundError(name_pattern)


def meta_filename(src_dir):
    os.chdir(src_dir)
    for file in glob.glob("*MTL.json"):
        return file
    raise FileNotFoundError("*MTL.json")


def _to_uint8(image, display_min, display_max):
    image = np.array(image, copy=True)
    image.clip(display_min, display_max, out=image)
    image -= display_min
    np.floor_divide(image, (display_max - display_min + 1) / 256,
                    out=image, casting='unsafe')
    return image.astype(np.uint8)


def to_uint8_lut(image, display_min, display_max):
    """
    Convert to uint8 and with histogram stretching (to improve contrast)
    lut stands for Look-up table - it's used to improve performance
    see https://stackoverflow.com/questions/14464449/
    using-numpy-to-efficiently-convert-16-bit-image-data-to-8-bit-for-display-with
    :param image: 
    :param display_min: 
    :param display_max: 
    :return: 
    """
    lut = np.arange(2 ** 16, dtype='uint16')
    lut = _to_uint8(lut, display_min, display_max)
    result = np.take(lut, image)
    return result


@contextmanager
def get_band(src_dir, band_number):
    band_path = band_filename(src_dir, band_number)
    band = rasterio.open(band_path)
    yield band
    band.close()


def calculate_ndvi(src_dir, dst_path, x0=None, x1=None, y0=None, y1=None, with_cloud_mask=False, is_pre_collection=False):
    with get_band(src_dir, bands.R) as r_band:
        with get_band(src_dir, bands.NIR) as nir_band:
            if not (x0 and x1 and y0 and y1):
                x0, y0 = 0, 0
                x1, y1 = r_band.shape
            r = r_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
            nir = nir_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
            ndvi = np.true_divide((nir - r), (nir + r))

            if with_cloud_mask:
                mask = get_cloud_mask(src_dir, is_pre_collection=is_pre_collection)
                ndvi[mask] = np.nan

            with rasterio.open(dst_path, 'w',
                               driver='GTiff', width=y1 - y0, height=x1-x0, count=1, blockxsize=512, blockysize=512,
                               dtype=np.float32, crs=r_band.crs, transform=r_band.transform, nodata=np.nan) as dst:
                for k, arr in [(1, ndvi)]:
                    dst.write(arr, indexes=k)


def calculate_rgb(src_dir, dst_path, display_min=5000,
                  display_max=13000, x0=None, x1=None, y0=None, y1=None,
                  with_cloud_mask=False, is_pre_collection=False):

    with get_band(src_dir, bands.R) as r_band:
        with get_band(src_dir, bands.G) as g_band:
            with get_band(src_dir, bands.B) as b_band:
                if not (x0 and x1 and y0 and y1):
                    x0, y0 = 0, 0
                    x1, y1 = r_band.shape
                r = to_uint8_lut(r_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)
                g = to_uint8_lut(g_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)
                b = to_uint8_lut(b_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)

                # if with_cloud_mask:
                #     cloud_mask = ~get_cloud_mask(src_dir)
                #     r, g, b = (band * cloud_mask for band in (r, g, b))
                cloud_mask = ~get_cloud_mask(src_dir, is_pre_collection=is_pre_collection)
                alpha = cloud_mask.astype(np.uint8) * 255
                alpha[r == 0] = 0

                with rasterio.open(dst_path, 'w',
                                   driver='GTiff', width=y1-y0, height=x1-x0, count=4, tiled=True,
                                   blockxsize=512, blockysize=512, compress=None, dtype=np.uint8,
                                   crs=r_band.crs, transform=r_band.transform, nodata=255) as dst:
                    for k, arr in [(1, r), (2, g), (3, b), (4, alpha)]:
                        dst.write(arr, indexes=k)


def calculate_ts(src_dir, dst_path, with_cloud_mask=True, is_pre_collection=False):


    brightness_temp.calculate_landsat_brightness_temperature(src_path=band_filename(src_dir, bands.TIRS),
                                                             src_mtl=meta_filename(src_dir),
                                                             dst_path=dst_path,
                                                             creation_options={},
                                                             temp_scale='C',
                                                             band=10,
                                                             processes=1,
                                                             dst_dtype='float32')
    if with_cloud_mask:
        cloud_mask = get_cloud_mask(src_dir, is_pre_collection=is_pre_collection)
        with rasterio.open(dst_path, mode='r+', nodata=np.nan) as src:
            band = src.read(1)
            band[cloud_mask] = np.nan
            src.write_band(1, band)


if __name__ == "__main__":
    ROOT = "/home/piotrek/mgr/datasets/"

    data_sets = [#'2015_04_21__LC81900222015111LGN00',
                 'LC08_L1TP_190022_20170731_20170801_01_RT']

    for data_set in data_sets:
        print("Calculating set: "+data_set)
        input_dirpath = ROOT + data_set + "/sources/"
        prefix = data_set.split("__")[-1]

        calculate_ts(src_dir=input_dirpath, dst_path=prefix + 'TEMP.tif', with_cloud_mask=True)

