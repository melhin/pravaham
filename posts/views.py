# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from posts.models import Post
from posts.publisher import produce


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
    return render(
        request,
        "posts/lobby.html",
        context={"messages": messages},
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
