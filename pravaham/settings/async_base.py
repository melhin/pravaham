from .base import *  # noqa


ROOT_URLCONF = "pravaham.urls.async_urls"
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
INSTALLED_APPS = INSTALLED_APPS + ["realtime"]  # noqa
