from django.shortcuts import render
import const
# Create your views here.
def home_page(request):
    return render(request, 'base.html', context={"geoserver_url":const.GEOSERVER_URL})