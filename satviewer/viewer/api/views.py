import os

from django.db.models import Min, Max
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from multiprocessing import Process

from aws.sqs import send_image_requested, JobMessage
from viewer.models import SatelliteImage, add_sentinel_images, add_landsat_images
from .serializers import SatelliteImageSerializer
import const
from processing.windows import get_tsvi, TsViData, get_image


class ImagesListAPIView(ListAPIView):
    serializer_class = SatelliteImageSerializer

    def get_queryset(self):
        queryset = SatelliteImage.objects.all()
        if self.request.query_params:
            clouds_min = float(self.request.query_params.get('clouds_min', 0))
            clouds_max = float(self.request.query_params.get('clouds_max', 100))
            data_min = float(self.request.query_params.get('data_min', 0))
            data_max = float(self.request.query_params.get('data_max', 100))
            date_min = self.request.query_params.get('date_min', None)
            date_max = self.request.query_params.get('date_max', None)
            print(clouds_min, clouds_max, data_min, data_max, date_min, date_max, end=" ")
            queryset = queryset.filter(clouds_percentage__range=(clouds_min, clouds_max),
                                       data_percentage__range=(data_min, data_max),
                                       date__range=(date_min, date_max))
        return queryset


class DateRangeView(APIView):
    def get(self, request, format=None):
        min_max = SatelliteImage.objects.all().values_list('date').aggregate(Min('date'), Max('date'))
        return Response(min_max)


class SingleImageView(APIView):

    def get(self, request, format=None):
        image_uri = request.query_params.get('image_uri')
        if image_uri:
            source = const.SENTINEL if image_uri.startswith('tiles') else const.LANDSAT
            message = JobMessage(source=source, img_uri=image_uri, process=const.RGB)
            message_id = send_image_requested(message)
            return Response({"message_id":message_id["MessageId"]})
        return Response({"message_id":"Bad Request"})


class AddSentinelImagesView(APIView):
    """API endpoint to look for all currently available 
    Sentinel scenes for Pomeranian disctrict."""
    def get(self, request, format=None):
        add_sentinel_images()
        return Response(status=status.HTTP_200_OK)


class AddLandsatImagesView(APIView):
    """API endpoint to look for all currently available 
        Landsat scenes for Pomeranian disctrict."""
    def get(self, request, format=None):
        add_landsat_images()
        return Response(status=status.HTTP_200_OK)

from rest_framework import serializers

class TsViSerializer(serializers.Serializer):
    points = serializers.ListField()
    downsampled = serializers.BooleanField()
    step = serializers.IntegerField()
    downsampled_size = serializers.IntegerField()
    original_size = serializers.IntegerField()

class WindowedTSVI(APIView):

    def get(self, request, format=None):
        data = request.query_params
        ne_lat, ne_lng, sw_lat, sw_lng = [float(i) for i in [data['neLat'], data['neLng'], data['swLat'], data['swLng']]]
        image_id = data['imageId']
        dataset_path = os.path.join(const.GEOSERVER_STORAGE, image_id, image_id.split('__')[-1])
        tsvi_data = get_tsvi(dataset_path, ne_lat=ne_lat, ne_lng=ne_lng, sw_lat=sw_lat, sw_lng=sw_lng) # type: TsViData
        d = TsViSerializer(tsvi_data).data
        return Response(data=d, status=status.HTTP_200_OK)

class WindowedRGBImage(APIView):
    """
    Returns a PNG file of RGB image for the selected bounding box
    """
    def get(self, request, format=None):
        data = request.query_params
        ne_lat, ne_lng, sw_lat, sw_lng = [float(i) for i in
                                          [data['neLat'], data['neLng'], data['swLat'], data['swLng']]]
        image_id = data['imageId']
        dataset_path = os.path.join(const.GEOSERVER_STORAGE, image_id, image_id.split('__')[-1])
        png_data = get_image(dataset_path, ne_lat=ne_lat, ne_lng=ne_lng, sw_lat=sw_lat, sw_lng=sw_lng)
        response = HttpResponse(content_type="image/png")
        response.write(png_data)
        return response



class AddNewImageView(APIView):
    def get(self, request, format=None):
        from add_images import add_image_set

        image_uri = request.query_params.get('image_uri')

        if image_uri:
            #add_image_set(image_uri)
            process = Process(target=add_image_set, args=(image_uri,))
            process.start()
            return Response({"result":"IMAGE PROCESSING STARTED"})
        return Response({"message_id":"Bad Request"})



