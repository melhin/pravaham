from django.urls import path

from realtime.views import get_new_content, stream_content, stream_new_content_notification, stream_posts

app_name = "realtime"

urlpatterns = [
    path("posts/", stream_posts, name="stream"),
    path("content/stream/", stream_content, name="content"),
    path("content/notifications/", stream_new_content_notification, name="content"),
    path("content/new/<str:last_id>/", get_new_content, name="new-content"),
]
