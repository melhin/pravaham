DJANGO_SETTINGS_MODULE=pravaham.settings.async_base uvicorn --reload pravaham.asgi:application --port 6767 --timeout-graceful-shutdown=0