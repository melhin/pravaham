import json
import logging
import urllib
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from posts.data import DataToSend, EventType
from posts.external import (
    get_last_messages_from_stream,
    get_last_seen,
    get_messages_from_stream,
    new_post_notification,
    set_last_seen,
)
from posts.models import Post

logger = logging.getLogger(__name__)


@login_required
def post_create(request):
    if request.method == "POST":
        text = request.POST["text"]
        post = Post.objects.create(text=text, creator=request.user)
        new_post_notification(
            DataToSend(
                event_type=EventType.NEW_POST.value,
                event_at=post.created_at.isoformat(),
                text=text,
            )
        )
        return redirect(reverse("posts:create"))
    else:
        return render(request, "posts/create.html")


@login_required
def lobby(request: HttpRequest) -> HttpResponse:
    messages = []
    for post in Post.objects.select_related("creator").all().order_by("-id")[:5]:
        messages.append(
            {
                "text": post.text,
                "creator__email": post.creator.email,
                "created_at": post.created_at.isoformat(),
            }
        )
    stream_server = urllib.parse.urljoin(
        settings.STREAM_SERVER, reverse("posts:content-notifications")
    )
    return render(
        request,
        "posts/lobby.html",
        context={"messages": messages, "stream_server": stream_server},
    )


@login_required
def new_posts(request: HttpRequest, from_date: str) -> HttpResponse:
    messages = []
    for post in (
        Post.objects.select_related("creator")
        .filter(created_at__gte=from_date)
        .order_by("-id")
    ):
        messages.append(
            {
                "text": post.text,
                "creator__email": post.creator.email,
                "created_at": post.created_at.isoformat(),
            }
        )
    return render(
        request,
        "posts/new_posts.html",
        context={"messages": messages},
    )


def content(request: HttpRequest) -> HttpResponse:
    stream_server = urllib.parse.urljoin(settings.STREAM_SERVER, "/realtime")
    messages_from_stream = get_last_messages_from_stream()
    messages_from_stream.reverse()
    messages = []
    for ele in messages_from_stream:
        post = json.loads(ele[1][b"v"])
        messages.append(
            {
                "text": post["content"].replace('class="invisible"', ""),
                "creator": post["account"],
                "created_at": post["created_at"],
            }
        )
    return render(
        request,
        "realtime/content.html",
        context={"stream_server": stream_server, "messages": messages},
    )


@login_required
def content_htmx(request: HttpRequest) -> HttpResponse:
    stream_server = urllib.parse.urljoin(settings.STREAM_SERVER, "/posts")
    messages_from_stream = get_messages_from_stream(last_id=None)
    messages = []
    if messages_from_stream:
        set_last_seen(
            uuid=request.user.uuid, last_seen=messages_from_stream[0][0].decode("utf-8")
        )
    for ele in messages_from_stream:
        post = json.loads(ele[1][b"v"])
        messages.append(
            {
                "text": post["content"].replace('class="invisible"', ""),
                "creator": post["account"],
                "created_at": post["created_at"],
            }
        )
    return render(
        request,
        "posts/content_htmx.html",
        context={"stream_server": stream_server, "messages": messages},
    )


def iso_to_epoch(iso_str):
    """Convert ISO formatted string to Unix timestamp"""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.timestamp()


def epoch_to_iso(epoch):
    """Convert Unix timestamp to ISO formatted string"""
    dt = datetime.fromtimestamp(float(epoch))
    return dt.isoformat() + "Z"


@login_required
def get_new_content(request: HttpRequest, *args, **kwargs):
    last_id = get_last_seen(uuid=request.user.uuid)
    messages = []
    if last_id:
        from_date = epoch_to_iso(last_id)
        logger.info(from_date)
        latest_post = None
        for post in (
            Post.objects.select_related("creator")
            .filter(created_at__gt=from_date)
            .order_by("-id")
        ):
            if not latest_post:
                latest_post = post.created_at.isoformat()
            messages.append(
                {
                    "text": post.text,
                    "creator__email": post.creator.email,
                    "created_at": post.created_at.isoformat(),
                }
            )
        set_last_seen(
            uuid=request.user.uuid,
            last_seen=iso_to_epoch(latest_post),
        )
    return render(
        request,
        "posts/new_posts.html",
        context={"messages": messages},
    )
