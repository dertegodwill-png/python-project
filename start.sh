#!/bin/sh
set -e

# Run migrations and collect static files, then start Gunicorn.
# This helps ensure the DB schema exists after deploy.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn betting_tracker.wsgi:application --bind 0.0.0.0:$PORT
