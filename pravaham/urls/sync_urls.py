from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html"), name='index'),
    path("accounts/", include('accounts.urls')),
    path("posts/", include('posts.urls')),
    path("admin/", admin.site.urls),
]
