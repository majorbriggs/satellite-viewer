from django.db.models import Model, TextField, FloatField, DateField


class SatelliteImage(Model):

    aws_bucket_uri = TextField()

    clouds_percentage = FloatField()

    data_percentage = FloatField()

    date = DateField()
