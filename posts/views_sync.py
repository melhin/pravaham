import logging
import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from posts.data import DataToSend, EventType
from posts.external import (
    get_last_five_posts_for_user,
    get_new_posts_for_user,
    new_post_notification,
)
from posts.models import Post
from posts.utils import get_all_emails_from_text

logger = logging.getLogger(__name__)


@login_required
def post_create(request):
    if request.method == "POST":
        text = request.POST["text"]
        user_emails_to_be_notified = get_all_emails_from_text(text)
        post = Post.objects.create(
            text=text, creator=request.user, tags=user_emails_to_be_notified
        )
        data_to_send = DataToSend(
            event_type=EventType.NEW_POST.value,
            event_at=post.created_at.isoformat(),
            text=text,
        )
        if user_emails_to_be_notified:
            new_post_notification(
                user_emails_to_be_notified=user_emails_to_be_notified,
                data_to_send=data_to_send,
            )
        return redirect(reverse("posts:create"))
    else:
        return render(request, "posts/create.html")


@login_required
@require_http_methods(["GET"])
def lobby(request: HttpRequest) -> HttpResponse:
    stream_server = urllib.parse.urljoin(
        settings.STREAM_SERVER, "/stream/content/notifications/"
    )
    messages = get_last_five_posts_for_user(user=request.user)
    return render(
        request,
        "posts/lobby.html",
        context={"messages": messages, "stream_server": stream_server},
    )


@login_required
@require_http_methods(["GET"])
def get_new_content(request: HttpRequest, *args, **kwargs):
    messages = get_new_posts_for_user(user=request.user)
    return render(
        request,
        "posts/new_posts.html",
        context={"messages": messages},
    )
