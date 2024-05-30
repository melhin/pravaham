from django.urls import path

from posts.views_async import (
    stream_new_content_notification,
)

app_name = "posts"

urlpatterns = [
    path(
        "content/notifications/",
        stream_new_content_notification,
        name="content-notifications",
    ),
]