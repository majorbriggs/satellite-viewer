from rest_framework.generics import ListAPIView

from viewer.models import SatelliteImage
from .serializers import SatelliteImageSerializer

class ImagesListAPIView(ListAPIView):

    queryset = SatelliteImage.objects.all()
    serializer_class = SatelliteImageSerializer