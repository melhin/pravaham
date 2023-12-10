from django.urls import include, path

urlpatterns = [
    path("realtime/", include("realtime.urls")),
]
