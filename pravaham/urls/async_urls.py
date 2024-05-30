from django.urls import include, path

urlpatterns = [
    path("stream/", include("posts.urls_async")),
]
