#!/bin/bash

# Render start script for Django app
export DJANGO_SETTINGS_MODULE=fitness_tracker.settings
exec gunicorn fitness_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
