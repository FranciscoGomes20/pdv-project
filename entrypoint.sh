#!/bin/sh

export LANG=en_US.UTF-8
export LANGUAGE=en_US:en
export LC_ALL=en_US.UTF-8

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

echo "Applying database migrations..."
set -e
python manage.py migrate
set +e

echo "Starting Django API with Gunicorn..."
exec "$@"