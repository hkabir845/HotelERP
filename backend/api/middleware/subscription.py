"""Subscription enforcement for tenant users."""
from django.http import JsonResponse
from django.utils import timezone

from api.auth.jwt_utils import decode_token
from api.models import Tenant


# Paths that skip subscription checks
_SKIP_PREFIXES = (
    '/api/auth/login',
    '/api/auth/refresh',
    '/api/core/',
    '/api/public/',
    '/api/superadmin/',
    '/admin/',
)


def _bearer_payload(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '') or ''
    if not auth.startswith('Bearer '):
        return None
    return decode_token(auth[7:].strip())


class SubscriptionMiddleware:
    """
    Block tenant API access when subscription is expired or tenant inactive.
    Superadmins always pass. Resolves tenant from headers or JWT.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ''
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return self.get_response(request)

        if not path.startswith('/api/'):
            return self.get_response(request)

        payload = _bearer_payload(request)
        if payload and payload.get('is_superuser'):
            return self.get_response(request)

        tenant = getattr(request, 'tenant', None)
        if tenant is None and payload:
            tid = payload.get('tenant_id')
            if tid:
                tenant = Tenant.objects.filter(id=tid).first()
                request.tenant = tenant

        if not tenant:
            return self.get_response(request)

        if not tenant.is_active:
            return JsonResponse(
                {
                    'detail': 'This business account is inactive.',
                    'code': 'tenant_inactive',
                },
                status=403,
            )

        if tenant.subscription_expires_at and tenant.subscription_expires_at < timezone.now():
            return JsonResponse(
                {
                    'detail': 'Subscription expired. Please renew your plan from the SaaS control panel.',
                    'code': 'subscription_expired',
                },
                status=402,
            )

        return self.get_response(request)


def tenant_subscription_active(tenant: Tenant) -> bool:
    if not tenant:
        return True
    if not tenant.is_active:
        return False
    if tenant.subscription_expires_at and tenant.subscription_expires_at < timezone.now():
        return False
    return True
