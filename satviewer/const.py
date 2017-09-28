from satviewer.settings import PRODUCTION

NDVI = 'NDVI'
RGB = 'RGB'
TEMP = 'TEMP'
LANDSAT = 'landsat'
SENTINEL = 'sentinel'
OUTPUT_BUCKET = 'satellite-viewer-processed'
WORKSPACE = "sat-viewer"
PRODUCTION_GEOSERVER_STORAGE = 'file:///home/ubuntu/sat-images/'
PRODUCTION_GEOSERVER = 'http://satellite-viewer.pl:8080/geoserver/'


GEOSERVER_STORAGE = PRODUCTION_GEOSERVER_STORAGE if PRODUCTION else 'file:///home/piotrek/mgr/datasets/'
GEOSERVER_URL = PRODUCTION_GEOSERVER if PRODUCTION else "http://localhost:8080/geoserver/"

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
GEOSERVER_USERNAME = ""
GEOSERVER_PASSWORD = ""
DATA_ROOT = '/home/ubuntu/sat-images/'


