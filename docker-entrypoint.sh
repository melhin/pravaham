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
            exec gunicorn pravaham.asgi:application -c uvicorn.conf.py --worker-class uvicorn.workers.UvicornWorker 
            ;;
        runfeed)
            echo "Starting mastadon feed"
            python ./manage.py get_mastodon_feed --domain https://streaming.mastodon.online/
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
done