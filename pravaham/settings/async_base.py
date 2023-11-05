from .base import *  # noqa


ROOT_URLCONF = "pravaham.urls.async_urls"
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

#ASYNC_APPS = [
#    "realtime",
#    "accounts", "posts"]
#]
#
#INSTALLED_APPS = [
#    "django.contrib.admin",
#    "django.contrib.auth",
#    "django.contrib.contenttypes",
#    "django.contrib.sessions",
#    *ASYNC_APPS,
#]
#