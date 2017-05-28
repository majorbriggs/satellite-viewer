from django.contrib import admin

from viewer.models import SatelliteImage



@admin.register(SatelliteImage)
class SatelliteImage(admin.ModelAdmin):
    list_display = ('aws_bucket_uri', 'clouds_percentage', 'data_percentage', 'date')