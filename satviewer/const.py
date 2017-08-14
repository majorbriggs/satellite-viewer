from satviewer.settings import PRODUCTION

NDVI = 'ndvi'
RGB = 'rgb'
LANDSAT = 'landsat'
SENTINEL = 'sentinel'
OUTPUT_BUCKET = 'satellite-viewer-processed'
WORKSPACE = "sat-viewer"
PRODUCTION_GEOSERVER_STORAGE = 'file:///home/ubuntu/sat-images/'

GEOSERVER_STORAGE = PRODUCTION_GEOSERVER_STORAGE if PRODUCTION else 'file:///home/piotrek/mgr/datasets/'



