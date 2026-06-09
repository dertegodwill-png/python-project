#!/bin/sh
set -e

# Use unbuffered output so logs appear immediately in Railway
PYTHON=python
if command -v python3 >/dev/null 2>&1; then
	PYTHON=python3
fi

# Retry migrations a few times to tolerate ephemeral startup ordering issues.
RETRIES=3
COUNT=0
until [ "$COUNT" -ge "$RETRIES" ]; do
	echo "Running migrations attempt $((COUNT+1))/$RETRIES"
	$PYTHON -u manage.py migrate --noinput && break
	COUNT=$((COUNT+1))
	sleep 2
done

echo "Collecting static files"
$PYTHON -u manage.py collectstatic --noinput

echo "Starting Gunicorn"
exec gunicorn betting_tracker.wsgi:application --bind 0.0.0.0:$PORT
