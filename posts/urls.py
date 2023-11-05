from django.urls import path

from posts.views import lobby, new_posts, post_create

app_name = "posts"

urlpatterns = [
    path("create/", post_create, name="create"),
    path("lobby/", lobby, name="lobby"),
    path("new/<str:from_date>/", new_posts, name="new_posts"),
]
