from django.contrib import admin

from viewer.models import SatelliteImage



@admin.register(SatelliteImage)
class SatelliteImage(admin.ModelAdmin):
    list_display = ('source', 'aws_bucket_uri', 'clouds_percentage', 'data_percentage', 'date')