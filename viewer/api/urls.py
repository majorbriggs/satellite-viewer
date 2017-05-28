from django.conf.urls import url

from viewer.api.views import ImagesListAPIView


urlpatterns = [
    url(r'^$', ImagesListAPIView.as_view(), name='images-list')
]

