from collections import namedtuple
from contextlib import contextmanager

from rio_toa import brightness_temp
import glob, os
import rasterio
import numpy as np
from l8qa.qa import cloud_confidence


Bands = namedtuple("Bands", ["R", "G", "B", "NIR", "TIRS"])

bands = Bands(R=4, G=3, B=2, NIR=5, TIRS=10)


def get_cloud_mask(src_dir):
    with rasterio.open(band_filename(src_dir, 'QA')) as src:
        src_array = src.read(1)

        cloudmask = cloud_confidence(src_array) == 3
        return cloudmask

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
    raise FileNotFoundError("*_MTL.json")


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


def calculate_ndvi(src_dir, dst_path, x0=None, x1=None, y0=None, y1=None, with_cloud_mask=False):
    with get_band(src_dir, bands.R) as r_band:
        with get_band(src_dir, bands.NIR) as nir_band:
            if not (x0 and x1 and y0 and y1):
                x0, y0 = 0, 0
                x1, y1 = r_band.shape
            r = r_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
            nir = nir_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
            ndvi = np.true_divide((nir - r), (nir + r))

            if with_cloud_mask:
                ndvi = ndvi * ~get_cloud_mask(src_dir)

            with rasterio.open(dst_path, 'w',
                               driver='GTiff', width=y1 - y0, height=x1-x0, count=1, blockxsize=512, blockysize=512,
                               dtype=np.float32, crs=r_band.crs, transform=r_band.transform, nodata=0) as dst:
                for k, arr in [(1, ndvi)]:
                    dst.write(arr, indexes=k)


def calculate_rgb(src_dir, dst_path, display_min=5000,
                  display_max=13000, x0=None, x1=None, y0=None, y1=None,
                  with_cloud_mask=False):

    with get_band(src_dir, bands.R) as r_band:
        with get_band(src_dir, bands.G) as g_band:
            with get_band(src_dir, bands.B) as b_band:
                if not (x0 and x1 and y0 and y1):
                    x0, y0 = 0, 0
                    x1, y1 = r_band.shape
                r = to_uint8_lut(r_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)
                g = to_uint8_lut(g_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)
                b = to_uint8_lut(b_band.read(1, window=((x0, x1), (y0, y1))), display_min, display_max)

                if with_cloud_mask:
                    cloud_mask = ~get_cloud_mask(src_dir)
                    r, g, b = (band * ~cloud_mask for band in (r, g, b))

                with rasterio.open(dst_path, 'w',
                                   driver='GTiff', width=y1-y0, height=x1-x0, count=3, tiled=True,
                                   blockxsize=512, blockysize=512, compress=None, dtype=np.uint8,
                                   crs=r_band.crs, transform=r_band.transform) as dst:
                    for k, arr in [(1, r), (2, g), (3, b)]:
                        dst.write(arr, indexes=k)


def calculate_ts(src_dir, dst_path, with_cloud_mask=True):


    brightness_temp.calculate_landsat_brightness_temperature(src_path=band_filename(src_dir, bands.TIRS),
                                                             src_mtl=meta_filename(src_dir),
                                                             dst_path=dst_path,
                                                             creation_options={},
                                                             temp_scale='C',
                                                             band=10,
                                                             processes=1,
                                                             dst_dtype='float32')
    if with_cloud_mask:
        cloud_mask = get_cloud_mask(src_dir)
        with rasterio.open(dst_path, mode='r+') as src:
            band = src.read(1)
            band = band * ~cloud_mask
            src.write_band(1, band)


if __name__ == "__main__":
    ROOT = "/home/piotrek/mgr/datasets_fix/"

    data_sets = ['2015_04_21__LC81900222015111LGN00',
                 '2017_04_10__LC81900222017100LGN00',
                 '2017_05_12__LC81900222017132LGN00',
                 '2017_05_28__LC81900222017148LGN00']

    for data_set in data_sets:
        print("Calculating set: "+data_set)
        input_dirpath = ROOT + data_set
        prefix = data_set.split("__")[-1]

        calculate_ndvi(src_dir=input_dirpath, dst_path=prefix + 'NDVI.tif')
        calculate_rgb(src_dir=input_dirpath, dst_path=prefix + 'RGB.tif', display_min=5000, display_max=13000)

