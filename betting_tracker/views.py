from django.http import JsonResponse


def healthz(request):
    """Return 200 OK to signal the app is running.

    This endpoint is intentionally tiny and safe to call in production.
    """
    return JsonResponse({"status": "ok"})
