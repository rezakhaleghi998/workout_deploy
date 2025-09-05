#!/bin/bash

# Start script for Render deployment
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"
exec gunicorn fitness_tracker.wsgi:application --bind 0.0.0.0:$PORT
