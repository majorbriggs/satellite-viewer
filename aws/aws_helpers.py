import boto3
import botocore
import json
from collections import namedtuple


Image = namedtuple("AWSImageData", ['source', 'aws_bucket_uri', 'clouds_percentage', 'data_percentage', 'date'])

SOURCE_SENTINEL = 'S2'
SOURCE_LANDSAT = 'L8'

sentinel_bucket_name = 'sentinel-s2-l1c'
landsat_bucket_name = 'landsat-pds'
landsat_prefix = 'L8/190/022'
s2_prefix = 'tiles/34/U/CF/'  # prefix for Pomeranian district

s3 = boto3.resource('s3', region_name='eu-central-1')
sentinel_bucket = s3.Bucket(sentinel_bucket_name)
landsat_bucket = s3.Bucket(landsat_bucket_name)

client = boto3.client('s3', region_name='eu-central-1',
                      config=botocore.client.Config(signature_version=botocore.UNSIGNED))


def get_s2_images_data(prefix=s2_prefix):

    result = client.list_objects(Bucket=sentinel_bucket_name,
                                 Prefix=prefix,
                                 Delimiter='/'
                                 )
    prefixes = result.get('CommonPrefixes') or []
    for o in prefixes:
        new_prefix = o.get('Prefix')
        depth = len(new_prefix.split('/'))
        if depth == 9:
            j = sentinel_bucket.Object(new_prefix + 'tileInfo.json').get()['Body']
            tile_info = json.loads(j.read().decode('utf-8'))
            yield Image(source=SOURCE_SENTINEL,
                        aws_bucket_uri=new_prefix,
                        clouds_percentage=tile_info['cloudyPixelPercentage'],
                        data_percentage=tile_info.get('dataCoveragePercentage'),
                        date=tile_info['timestamp'].split('T')[0])
        else:
            for obj in get_s2_images_data(prefix=new_prefix):
                yield obj


def get_landsat_images_data(prefix=landsat_prefix):
    result = client.list_objects(Bucket=landsat_bucket_name,
                                 Prefix=prefix,
                                 Delimiter='/'
                                 )
    prefixes = result.get('CommonPrefixes') or []
    for o in prefixes:
        new_prefix = o.get('Prefix')
        depth = len(new_prefix.split('/'))
        if depth == 5:
            scene_id = new_prefix.split('/')[-2]
            j = landsat_bucket.Object(new_prefix + scene_id + '_MTL.json').get()["Body"]
            tile_info = json.loads(j.read().decode('utf-8'))
            yield Image(source=SOURCE_LANDSAT,
                        aws_bucket_uri=new_prefix,
                        clouds_percentage=tile_info['L1_METADATA_FILE']['IMAGE_ATTRIBUTES']['CLOUD_COVER'],
                        data_percentage=100.0,
                        date=tile_info['L1_METADATA_FILE']['PRODUCT_METADATA']['DATE_ACQUIRED'])
        else:
            for obj in get_landsat_images_data(prefix=new_prefix):
                yield obj


if __name__ == '__main__':
    for i in get_landsat_images_data():
        print(i.aws_bucket_uri)
