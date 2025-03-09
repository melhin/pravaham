from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from pravaham.views import sync_health

urlpatterns = [
    path("posts/", include("posts.urls_sync")),
    path("admin/", admin.site.urls),
    path("health/", sync_health, name="sync_health"),
    path("", include("accounts.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
