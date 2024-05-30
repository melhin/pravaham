from django.urls import path

from posts.views_sync import get_new_content, lobby, post_create

app_name = "posts"

urlpatterns = [
    path("create/", post_create, name="create"),
    path("lobby/", lobby, name="lobby"),
    path("content/new/", get_new_content, name="new-content"),
]
