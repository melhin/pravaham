from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
async def async_health(request: HttpRequest, *args, **kwargs):
    return HttpResponse(status=200)

@require_http_methods(["GET"])
async def sync_health(request: HttpRequest, *args, **kwargs):
    return HttpResponse(status=200)