#!/bin/bash
set -eu

for arg in "$@"
do
    case "$arg" in
        main)
            echo "Running migration"
            python manage.py migrate --traceback
            echo "Starting sync server"
            exec gunicorn -c gunicorn.conf.py pravaham.wsgi
            ;;
        async)
            echo "Starting async server"
            exec uvicorn pravaham.asgi:application --host 0.0.0.0 --port 8002  --workers 2 --timeout-graceful-shutdown 0
            ;;
        async-local)
            echo "Starting async server"
            export DJANGO_SETTINGS_MODULE=pravaham.settings.async_base
            exec uvicorn pravaham.asgi:application --port 8002 --reload --timeout-graceful-shutdown 0
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
done