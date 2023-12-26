import json
import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from posts.external import (
    get_last_messages_from_stream,
    get_last_seen,
    get_messages_from_stream,
    produce,
    set_last_seen,
)
from posts.models import Post


@login_required
def post_create(request):
    if request.method == "POST":
        text = request.POST["text"]
        post = Post.objects.create(text=text, creator=request.user)
        produce(
            message={
                "type": "notification.type.new_post",
                "created_at": post.created_at.isoformat(),
            }
        )
        return redirect(reverse("posts:create"))
    else:
        return render(request, "posts/create.html")


@login_required
def lobby(request: HttpRequest) -> HttpResponse:
    messages = []
    for post in Post.objects.select_related("creator").all().order_by("-id"):
        messages.append(
            {
                "text": post.text,
                "creator__email": post.creator.email,
                "created_at": post.created_at.isoformat(),
            }
        )
    stream_server = urllib.parse.urljoin(settings.STREAM_SERVER, "/realtime/posts/")
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
    stream_server = urllib.parse.urljoin(settings.STREAM_SERVER, "/realtime")
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
        "realtime/content_htmx.html",
        context={"stream_server": stream_server, "messages": messages},
    )


@login_required
def get_new_content(request: HttpRequest, last_id: str | None = None, *args, **kwargs):
    last_id = get_last_seen(uuid=request.user.uuid)
    messages = []
    if last_id:
        messages_from_stream = get_messages_from_stream(last_id=last_id.decode("utf-8"))
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
        "realtime/new_posts.html",
        context={"messages": messages},
    )
