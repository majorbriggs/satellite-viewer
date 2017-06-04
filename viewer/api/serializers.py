from rest_framework.serializers import ModelSerializer

from viewer.models import SatelliteImage

class SatelliteImageSerializer(ModelSerializer):

    class Meta:
        model = SatelliteImage
        fields = ['source',
                  'aws_bucket_uri',
                  'data_percentage',
                  'clouds_percentage',
                  'date']

