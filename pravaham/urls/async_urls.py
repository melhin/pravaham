from django.urls import include, path
from pravaham.views import async_health

urlpatterns = [
    path("health/", async_health, name="async_health"),
    path("stream/", include("posts.urls_async")),
]
