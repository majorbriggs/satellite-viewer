from django.shortcuts import render
from django.conf import settings

# Create your views here.
def home_page(request):
    return render(request, 'base.html', context={"geoserver_url":settings.GEOSERVER_URL})