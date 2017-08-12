import math
import rasterio
from django.http import HttpResponse
from pyproj import Proj
import pyproj
from collections import namedtuple
import rasterio.transform as rtrans
from affine import Affine
import os

from rasterio import MemoryFile

LngLat = namedtuple("LngLat", ['lng', 'lat'])


class LngLatWindow:
    wgs84 = Proj(proj='latlon', datum='WGS84')

    def __init__(self, src, north_east: LngLat, south_west: LngLat):
        self.north_east = north_east
        self.south_west = south_west
        self.crs = Proj(src.crs)
        self.transform = src.transform  # type: Affine
        self.projected_ne = self._get_projected_from_lnglat(self.north_east)
        self.projected_sw = self._get_projected_from_lnglat(self.south_west)

    def _get_projected_from_lnglat(self, lnglat):
        px, py = pyproj.transform(self.wgs84, self.crs, *lnglat)
        return px, py

    def get_rasterio_window(self):
        rowcol_top = rtrans.rowcol(transform=self.transform, xs=self.projected_ne[0], ys=self.projected_ne[1])
        rowcol_bottom = rtrans.rowcol(transform=self.transform, xs=self.projected_sw[0], ys=self.projected_sw[1])
        col_start, col_stop = rowcol_bottom[1], rowcol_top[1]
        row_start, row_stop = rowcol_top[0], rowcol_bottom[0]
        window = ((row_start, row_stop), (col_start, col_stop))
        return window


class TsViData:

    def __init__(self, points, downsampled, step, original_size):
        self.points = points
        self.downsampled = downsampled
        self.step = step
        self.downsampled_size = len(points)
        self.original_size = original_size


def get_tsvi(dataset_path, neLng, neLat, swLng, swLat, max_n=10000):
    downsampled = False
    step = None
    ts_file = dataset_path + "_TEMP.tif"
    ndvi_file = dataset_path + "_NDVI.tif"
    with rasterio.open(ts_file) as ts_src, rasterio.open(ndvi_file) as ndvi_src:
        lnglatWin = LngLatWindow(ts_src, north_east=LngLat(lng=neLng, lat=neLat),
                                 south_west=LngLat(lng=swLng, lat=swLat))
        raster_window = lnglatWin.get_rasterio_window()
        ndvi_points = ndvi_src.read(1, window=raster_window)
        ts_points = ts_src.read(1, window=raster_window)
        ts_list = ts_points.flatten().tolist()
        ndvi_list = ndvi_points.flatten().tolist()

        if max_n is not None and len(ndvi_list) > max_n:
            downsampled = True
            step = math.ceil(len(ndvi_list) / max_n)
            ndvi_downsampled = ndvi_list[::step]
            ts_downsampled = ts_list[::step]
            points = list(zip(ndvi_downsampled, ts_downsampled))
        else:
            points = list(zip(ndvi_list, ts_list))
        return TsViData(original_size=len(ndvi_list), points=points, downsampled=downsampled, step=step)

def get_image(dataset_path, neLng, neLat, swLng, swLat):
    rgb_file = dataset_path + "_RGB.tif"
    with rasterio.open(rgb_file) as rgb_src:
        lnglatWin = LngLatWindow(rgb_src, north_east=LngLat(lng=neLng, lat=neLat),
                                 south_west=LngLat(lng=swLng, lat=swLat))
        raster_window = lnglatWin.get_rasterio_window()
        rgb_points = rgb_src.read(window=raster_window)
        height, width = get_witdh_height_from_window(raster_window)
        with MemoryFile() as memfile:
            with memfile.open(driver='PNG', count=3, width=width, height=height, dtype='uint8') as dataset:
                dataset.write(rgb_points)

            return memfile.read()

def get_witdh_height_from_window(window):
    return abs(window[0][1]-window[0][0]), abs(window[1][1] - window[1][0])
if __name__ == "__main__":
    get_image("test", 55, 56, 18, 19)