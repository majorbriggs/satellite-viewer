To set up the application locally:
======================================

1. Do the common steps for Valid for both section
2. Make sure the variable production in settings.py is False
3. Run the application with python manage.py runserver, make sure to create a superuser for the database

To set up the application on AWS:
====================================
1. Create an instance (the tiny one is to weak for the application, I used xlarge General purpouse type)
2. install the dependencies from initial.sh
2. Do the steps from Valid for both section
3. Install mod_wsgi and run the Django App on it
4. Make sure the app uses the correct server URLs for the AJAX calls (check paths in const.py and Javascript code in static folder)
5. Set production variable in settings.py to True

Valid for both
================
1. Install and run GeoServer
2. Set up paths and API keys in const.py
3. pip install all python requirements from requirements.txt

