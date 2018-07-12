#!/usr/bin/env bash

python manage.py makemigrations --noinput --settings=$DJANGO_SETTINGS_MODULE

#run the Django command-line utility to create the database tables automatically
python manage.py migrate --noinput --settings=$DJANGO_SETTINGS_MODULE

python manage.py create_admin_user --settings=$DJANGO_SETTINGS_MODULE

python manage.py runserver 0.0.0.0:8081 --settings=$DJANGO_SETTINGS_MODULE
