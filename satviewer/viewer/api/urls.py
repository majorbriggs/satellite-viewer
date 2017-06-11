from django.conf.urls import url

from viewer.api.views import (
    ImagesListAPIView,
    DateRangeView,
    SingleImageView,
    AddLandsatImagesView,
    AddSentinelImagesView)

urlpatterns = [
    url(r'images/$', ImagesListAPIView.as_view(), name='images-list'),
    url(r'images/dates$', DateRangeView.as_view(), name='date-range'),
    url(r'image$', SingleImageView.as_view(), name='get-image'),
    url(r'images/add/sentinel$', AddSentinelImagesView.as_view(), name='add-images-sentinel'),
    url(r'images/add/landsat$', AddLandsatImagesView.as_view(), name='add-images-landsat'),

]

