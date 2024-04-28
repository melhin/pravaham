from django.urls import path

from realtime.views import stream_posts, stream_timer, stream_content, get_new_content, stream_new_content_notification

app_name = "realtime"

urlpatterns = [
    path("posts/", stream_posts, name="stream"),
    path("content/stream/", stream_content, name="content-stream"),
    path(
        "content/notifications/",
        stream_new_content_notification,
        name="content-notifications",
    ),
    path("content/new/<str:last_id>/", get_new_content, name="new-content"),
    path("timer/", stream_timer, name="timer"),
]
