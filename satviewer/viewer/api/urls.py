from django.conf.urls import url

from viewer.api.views import (
    ImagesListAPIView,
    DateRangeView,
    AddNewImageView,
    AddLandsatImagesView,
    AddSentinelImagesView,
    WindowedTSVI,
    WindowedRGBImage)

urlpatterns = [
    url(r'images/$', ImagesListAPIView.as_view(), name='images-list'),
    url(r'images/dates$', DateRangeView.as_view(), name='date-range'),
    url(r'image$', AddNewImageView.as_view(), name='add-image'),
    url(r'images/add/sentinel$', AddSentinelImagesView.as_view(), name='add-images-sentinel'),
    url(r'images/add/landsat$', AddLandsatImagesView.as_view(), name='add-images-landsat'),
    url(r'tsvi$', WindowedTSVI.as_view(), name='tsvi'),
    url(r'windowed_image$', WindowedRGBImage.as_view(), name='windowed-image')

]

