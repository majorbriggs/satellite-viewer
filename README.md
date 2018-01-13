# Satellite Viewer


Web application based on GeoServer, Django, Leaflet, rasterio and numpy.
It allows to download, process and analyze satellite data from Sentinel-2 and Landsat 8 systems.
Based on the satellite data the app calculates so called Ts/VI plots (http://journals.sagepub.com/doi/abs/10.1177/0309133309338997) and allows the user to analyze sub-regions of the plot on the NDVI and Temperature layers of on the map.

The satellite data is obtained from the public AWS S3 buckets:
- http://sentinel-pds.s3-website.eu-central-1.amazonaws.com
- https://aws.amazon.com/public-datasets/landsat/

processed using rasterio and numpy libraries, and uploaded to a GeoServer instance from where the layers are served to the client app.

Done as part of my master thesis at Gdansk University of Technology.


## To set up the application locally:


1. Do the common steps for Valid for both section
2. Make sure the variable production in settings.py False
3. Run the application with python manage.py runserver, make sure to create a superuser for the database

## To set up the application on AWS:

1. Create an instance (the tiny one is to weak for the application, I used xlarge General purpouse type)
2. install the dependencies from initial.sh
2. Do the steps from Valid for both section
3. Install mod_wsgi and run the Django App on it
4. Make sure the app uses the correct server URLs for the AJAX calls (check paths in const.py and Javascript code in static folder)
5. Set production variable in settings.py to True

## Valid for both

1. Install and run GeoServer
2. Set up paths and AWS API keys in const.py
3. pip install all python requirements from requirements.txt

