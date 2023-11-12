from django.urls import path

from posts.views import content, lobby, new_posts, post_create

app_name = "posts"

urlpatterns = [
    path("create/", post_create, name="create"),
    path("lobby/", lobby, name="lobby"),
    path("content/", content, name="content"),
    path("new/<str:from_date>/", new_posts, name="new_posts"),
]
