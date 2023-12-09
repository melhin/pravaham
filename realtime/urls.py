from django.urls import path

from realtime.views import stream_content, stream_posts, get_new_content

app_name = "realtime"

urlpatterns = [
    path("posts/", stream_posts, name="stream"),
    path("content/", stream_content, name="content"),
    path("content/new/<str:last_id>", get_new_content, name="new-content"),
]
