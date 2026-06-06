import time
from django.core.cache import caches
from django.http import HttpResponse
from django.conf import settings


# Simple security headers middleware and a lightweight rate limiter for login


class SecurityHeadersMiddleware:
    """Add common security headers and a reasonably strict default CSP.

    The middleware is conservative by default to avoid breaking resources; adjust
    `CSP_DIRECTIVES` in settings.py if your app requires additional sources.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy - default safe directives; allow known CDN used in templates
        csp = getattr(settings, 'CSP_DIRECTIVES', None)
        if not csp:
            csp = (
                "default-src 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net; "
                "style-src 'self' https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "object-src 'none'; base-uri 'self'; frame-ancestors 'none';"
            )
        response.setdefault('Content-Security-Policy', csp)

        # Strong referrer policy and content-type sniffing protection
        response.setdefault('Referrer-Policy', getattr(settings, 'SECURE_REFERRER_POLICY', 'no-referrer'))
        response.setdefault('X-Content-Type-Options', 'nosniff')

        # Prevent clickjacking
        response.setdefault('X-Frame-Options', 'DENY')

        # Permissions-Policy (formerly Feature-Policy) - disable sensitive features by default
        response.setdefault('Permissions-Policy', "geolocation=(), microphone=(), camera=(), interest-cohort=()")

        # HSTS: if configured in settings and request is secure, ensure header is present
        try:
            hsts_seconds = int(getattr(settings, 'SECURE_HSTS_SECONDS', 0))
        except Exception:
            hsts_seconds = 0
        if hsts_seconds and request.is_secure():
            hsts = f"max-age={hsts_seconds}"
            if getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False):
                hsts += "; includeSubDomains"
            if getattr(settings, 'SECURE_HSTS_PRELOAD', False):
                hsts += "; preload"
            response.setdefault('Strict-Transport-Security', hsts)

        return response


class LoginRateLimitMiddleware:
    """Small rate limiter: limits POSTs to the login endpoint by IP and optionally username.

    This is intentionally lightweight and best suited for small deployments. For
    production, prefer a hardened solution (e.g., django-axes, fail2ban at the
    reverse-proxy, or cloud WAF rate-limiting).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = caches['default']
        # configurable via settings with safe defaults
        self.limit = getattr(settings, 'LOGIN_RATE_LIMIT', 5)
        self.window = getattr(settings, 'LOGIN_RATE_WINDOW', 60)

    def __call__(self, request):
        # Apply only to login POSTs. Adjust path as needed to match your login URL.
        if request.path.startswith('/users/login/') and request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            username = (request.POST.get('username') or '').strip() or 'anon'
            key = f'rl:{ip}:{username}'
            entry = self.cache.get(key) or {'count': 0, 'ts': time.time()}
            now = time.time()
            if now - entry['ts'] > self.window:
                entry = {'count': 0, 'ts': now}
            entry['count'] += 1
            self.cache.set(key, entry, timeout=self.window)
            if entry['count'] > self.limit:
                resp = HttpResponse('Too many login attempts. Try again later.', status=429)
                # Indicate when the client may try again
                resp['Retry-After'] = str(int(entry['ts'] + self.window - now))
                return resp
        return self.get_response(request)
