from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("posts/", include("posts.urls_sync")),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
