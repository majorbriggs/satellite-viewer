from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from viewer.models import SatelliteImage
from .serializers import SatelliteImageSerializer
from django.db.models import Min, Max


class ImagesListAPIView(ListAPIView):

    serializer_class = SatelliteImageSerializer

    def get_queryset(self):
        queryset = SatelliteImage.objects.all()
        if self.request.query_params:
            clouds_min = float(self.request.query_params.get('clouds_min', 0))
            clouds_max = float(self.request.query_params.get('clouds_max', 0))
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
		return Response("Success!")