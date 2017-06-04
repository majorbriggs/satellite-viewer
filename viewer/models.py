from django.db.models import Model, TextField, FloatField, DateField
from viewer.aws.aws_helpers import get_s2_images_data, get_landsat_images_data
from viewer.aws.aws_helpers import Image


class SatelliteImage(Model):

    aws_bucket_uri = TextField()

    clouds_percentage = FloatField()

    data_percentage = FloatField()

    date = DateField()

    def __str__(self):
        return "Image: {}, clouds: {}, data: {}, date: {}".format(self.aws_bucket_uri,
                                                                  self.clouds_percentage,
                                                                  self.data_percentage,
                                                                  self.date)


def add_image(image: Image):
        i = SatelliteImage()
        i.aws_bucket_uri = image.aws_bucket_uri
        i.data_percentage = image.data_percentage
        i.clouds_percentage = image.clouds_percentage
        i.date = image.date
        i.save()


def add_sentinel_images():
    for image in get_s2_images_data():
        print("Adding image {}".format(image.aws_bucket_uri))
        add_image(image)

def add_landsat_images():
    for image in get_landsat_images_data():
        print("Adding Landsat image {}".format(image.aws_bucket_uri))
        add_image(image)

if __name__ == "__main__":
    add_sentinel_images()