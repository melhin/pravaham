from django.urls import path

from realtime.live_qa import create_question, get_new_questions, questions, start_activity, stream_new_activity
from realtime.views import get_new_content, stream_content, stream_new_content_notification, stream_posts, stream_timer

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
    path("qa/listen/", stream_new_activity, name="qa-listen"),
    path("qa/send/", create_question, name="qa-send"),
    path("qa/create/", start_activity, name="qa-create"),
    path("qa/", questions, name="qa-start"),
    path("qa/new/<str:last_id_returned>/", get_new_questions, name="qa-new"),
]
