from django.conf.urls import url

from viewer.api.views import ImagesListAPIView, DateRangeView


urlpatterns = [
    url(r'^$', ImagesListAPIView.as_view(), name='images-list'),
    url(r'dates$', DateRangeView.as_view(), name='date-range')

]

