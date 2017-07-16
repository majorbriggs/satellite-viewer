import rasterio
from pyproj import Proj
import pyproj
from collections import namedtuple
import rasterio.transform as rtrans
from affine import Affine
import os


LngLat = namedtuple("LngLat", ['lng', 'lat'])



class LngLatWindow:
    wgs84 = Proj(proj='latlon', datum='WGS84')

    def __init__(self, src, north_east: LngLat, south_west: LngLat):
        self.north_east = north_east
        self.south_west = south_west
        self.crs = Proj(src.crs)
        self.transform = src.transform # type: Affine
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

def get_tsvi(dataset_path, neLng, neLat, swLng, swLat):
    ts_file = dataset_path + "_TEMP"
    ndvi_file = dataset_path + "_NDVI"
    with rasterio.open(ts_file) as ts_src, rasterio.open(ndvi_file) as ndvi_src:
        lnglatWin = LngLatWindow(ts_src, north_east=LngLat(lng=neLng, lat=neLat),
                         south_west=LngLat(lng=swLng, lat=swLat))
        raster_window = lnglatWin.get_rasterio_window()
        ndvi_points = ndvi_src.read(1, window=raster_window)
        ts_points = ts_src.read(1, window=raster_window)
        points = zip(ndvi_points.flatten().tolist(), ts_points.flatten().tolist())
        return points