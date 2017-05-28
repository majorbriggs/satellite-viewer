from rest_framework.serializers import ModelSerializer

from viewer.models import SatelliteImage

class SatelliteImageSerializer(ModelSerializer):

    class Meta:
        model = SatelliteImage
        fields = ['aws_bucket_uri',
                  'data_percentage',
                  'clouds_percentage',
                  'date']

