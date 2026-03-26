#!/bin/sh
set -e

# If a command is passed as argument (e.g. "celery ..."), run migrations then exec it.
# Otherwise run the default web server flow (migrate + collectstatic + gunicorn).
if [ "$1" = "celery" ]; then
    echo ">>> Applying database migrations (celery worker)..."
    python manage.py migrate --noinput
    exec "$@"
fi

echo ">>> Applying database migrations..."
python manage.py migrate --noinput

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput

echo ">>> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
