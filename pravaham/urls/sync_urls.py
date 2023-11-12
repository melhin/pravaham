from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("posts/", include('posts.urls')),
    path("admin/", admin.site.urls),
    path("", include('accounts.urls')),
]
