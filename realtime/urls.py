from django.urls import path

from realtime.views import stream_content, stream_posts

app_name = "realtime"

urlpatterns = [
    path("posts/", stream_posts, name="stream"),
    path("content/", stream_content, name="content"),
]
