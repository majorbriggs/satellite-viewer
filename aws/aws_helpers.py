import os

import boto3
import botocore
import json
from collections import namedtuple

import const
from aws.sqs import JobMessage

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


def download_sentinel_bands(bands, dir_uri, output_dir='.'):
    for band in bands:
        print()
        band_filename = "B{:>02}.jp2".format(band)
        file_key = dir_uri + band_filename
        output_filepath = os.path.join(output_dir, band_filename)
        client.download_file(sentinel_bucket_name, file_key, output_filepath)

def download_landsat_bands(bands, dir_uri, output_dir='.'):
    for band in bands:
        scene_id = dir_uri.strip('/').split('/')[-1]
        band_filename = scene_id+"_B{}.TIF".format(band)
        file_key = dir_uri + band_filename
        output_filepath = os.path.join(output_dir, "B{}.TIF".format(band))
        client.download_file(landsat_bucket_name, file_key, output_filepath)


def upload_to_s3(bucket_name, key, filepath):
    print("Uploading {} to S3 bucket {} as {}".format(filepath, bucket_name, key))
    with open(filepath, 'rb') as f:
        s3.Bucket(bucket_name).put_object(Key=key, Body=f)
    print("Upload finished")


def download_from_s3(bucket_name, key, filepath):
    print("Downloading from S3 bucket {} under key {} saving as {}".format(bucket_name, key, filepath))
    try:
        s3.Bucket(bucket_name).download_file(Key=key, Filename=filepath)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

if __name__ == '__main__':
    pass