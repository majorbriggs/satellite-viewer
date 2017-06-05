import subprocess
from contextlib import contextmanager
from enum import IntEnum
import os

import rasterio
import numpy as np

import const

from aws.aws_helpers import download_landsat_bands, download_sentinel_bands
from aws.sqs import JobMessage


class Bands(IntEnum):
    B = 2
    G = 3
    R = 4
    NIR = 8


class ImageCalculator:
    RGB_suffix = 'rgb'
    NDVI_suffix = 'ndvi'
    NDVI_bands = None
    RGB_bands = None
    # this should be calculated dynamically
    display_min = 0
    display_max = np.iinfo(np.uint16).max

    def __init__(self, image_uri, filename_template, default_width, default_height, process):
        self.filename_template = filename_template
        self.input_dir = "."
        self.default_width=default_width
        self.default_height=default_height
        self.process = process
        self.image_uri = image_uri
        self.output_filepath=self.process + '.tiff'


    @staticmethod
    def for_job(job: JobMessage):
        if job.source == const.LANDSAT:
            return LandsatCalculator(process=job.process, image_uri=job.img_uri)
        elif job.source == const.SENTINEL:
            return SentinelCalculator(process=job.process, image_uri=job.img_uri)
        else:
            raise RuntimeError("Message has a wrong source type {}".format(job.source))

    def get_files(self):
        raise NotImplementedError

    @contextmanager
    def get_band(self, band_number):
        path = os.path.join(self.input_dir, self.filename_template.format(band_number))
        band = rasterio.open(path)
        yield band
        band.close()

    def _to_uint8(self, image):
        display_min, display_max = self.display_min, self.display_max
        image = np.array(image, copy=True)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        np.floor_divide(image, (display_max - display_min + 1) / 256,
                        out=image, casting='unsafe')
        return image.astype(np.uint8)

    def to_uint8_lut(self, image):
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
        lut = self._to_uint8(lut)
        result = np.take(lut, image)
        return result


    def save_result(self, x0=0, y0=0, x1=None, y1=None):
        output_filepath = self.process+".tiff"
        if self.process == const.NDVI:
            return self.save_ndvi(output_filepath, x0, y0, x1, y1)
        elif self.process == const.RGB:
            return self.save_rgb(output_filepath, x0, y0, x1, y1)


    def save_rgb(self, output_filepath, x0=0, y0=0, x1=None, y1=None):

        if x1 is None:
            x1 = self.default_width
        if y1 is None:
            y1 = self.default_height

        with self.get_band(Bands.R) as r_band:
            with self.get_band(Bands.G) as g_band:
                with self.get_band(Bands.B) as b_band:
                    r = self.to_uint8_lut(r_band.read(1, window=((x0, x1), (y0, y1))))
                    g = self.to_uint8_lut(g_band.read(1, window=((x0, x1), (y0, y1))))
                    b = self.to_uint8_lut(b_band.read(1, window=((x0, x1), (y0, y1))))
                    with rasterio.open(output_filepath, 'w',
                                       driver='GTiff', width=x1-x0, height=y1-y0, count=3, tiled=True, blockxsize=512, blockysize=512,
                                       compress=None, dtype=r.dtype, crs=r_band.crs, transform=r_band.transform) as dst:
                        for k, arr in [(1, r), (2, g), (3, b)]:
                            dst.write(arr, indexes=k)
        if os.path.exists(output_filepath):
            return output_filepath
        else:
            raise FileNotFoundError("RGB processing failed. {} not found".format(output_filepath))

    def save_ndvi(self, output_filepath, x0=0, y0=0, x1=None, y1=None):
        if x1 is None:
            x1 = self.default_width
        if y1 is None:
            y1 = self.default_height

        with self.get_band(Bands.R) as r_band:
            with self.get_band(Bands.NIR) as nir_band:
                r = r_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
                nir = nir_band.read(1, window=((x0, x1), (y0, y1))).astype(np.float32)
                ndvi = np.true_divide((nir-r), (nir + r))
                output_band = np.rint((ndvi) * 255).astype(np.uint8)
                with rasterio.open(output_filepath, 'w',
                                   driver='GTiff', width=x1-x0, height=y1-y0, count=1,
                                   dtype=np.uint8, crs=r_band.crs, transform=r_band.transform, nodata=0) as dst:
                    for k, arr in [(1, output_band)]:
                        dst.write(arr, indexes=k)
        if os.path.exists(output_filepath):
            return output_filepath
        else:
            raise FileNotFoundError("NDVI processing failed. {} not found".format(output_filepath))


class LandsatCalculator(ImageCalculator):
    display_max = 10000
    display_min = 6000
    bands = {const.NDVI: [2, 5],
             const.RGB: [4, 3, 2]}

    def __init__(self, process, image_uri):
        super().__init__(process=process, image_uri=image_uri, filename_template='B{}.TIF', default_width=8131, default_height=8221)

    def get_files(self):
        download_landsat_bands(bands=self.bands[self.process], dir_uri=self.image_uri)

class SentinelCalculator(ImageCalculator):
    display_min = 1000
    display_max = 5000
    bands = {const.NDVI: [2, 8],
          const.RGB: [4, 3, 2]}

    def __init__(self, process, image_uri):
        super().__init__(process=process, image_uri=image_uri, filename_template='B{:0>2}.jp2', default_width=10980, default_height=10980)

    def get_files(self):
        download_sentinel_bands(bands=self.bands[self.process], dir_uri=self.image_uri)




def add_overviews(filepath, method='average', levels=None):
    print("Adding overviews to: {}".format(filepath))
    if levels is None:
        levels = [2, 4, 8, 16, 32]
        try:
            subprocess.check_call('gdaladdo -r {method} {filepath} {levels}'.format(
            method=method,
            filepath=filepath,
            levels=", ".join(map(str, levels))), shell=True
            )
            print("Overviews added.")
        except subprocess.CalledProcessError:
            print("Adding overviews to {} failed".format(filepath))