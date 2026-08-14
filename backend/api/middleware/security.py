"""Security middleware: rate limiting and security headers."""
from collections import defaultdict
from datetime import datetime, timedelta

from django.http import JsonResponse


class RateLimitMiddleware:
    """Rate limiting middleware (120 requests per minute per IP)."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_per_minute = 120
        self.requests = defaultdict(list)

    def __call__(self, request):
        client_ip = self._get_client_ip(request)
        now = datetime.now()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JsonResponse(
                {'detail': 'Rate limit exceeded. Please try again later.'},
                status=429,
            )

        self.requests[client_ip].append(now)
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class SecurityHeadersMiddleware:
    """Add security headers to responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
