"""Multi-tenant middleware for domain-based tenant routing."""
from django.conf import settings

from api.models import Tenant


def get_tenant_from_domain(domain, db=None):
    """Get tenant from domain or subdomain."""
    tenant = Tenant.objects.filter(
        models_q_domain(domain)
    ).first()
    if tenant and tenant.is_active:
        return tenant
    return None


def models_q_domain(domain):
    from django.db.models import Q
    return Q(domain=domain) | Q(subdomain=domain)


def get_current_tenant(request):
    """
    Get current tenant from request headers or host.
    Checks: X-Tenant-ID, X-Tenant-Subdomain, Host header.
    """
    tenant_id_header = getattr(settings, 'TENANT_ID_HEADER', 'X-Tenant-ID')
    tenant_header = getattr(settings, 'TENANT_HEADER', 'X-Tenant-Subdomain')

    tenant_id = request.META.get(f'HTTP_{tenant_id_header.upper().replace("-", "_")}')
    if tenant_id:
        try:
            tenant = Tenant.objects.filter(
                id=int(tenant_id),
                is_active=True,
            ).first()
            if tenant:
                return tenant
        except (ValueError, TypeError):
            pass

    tenant_subdomain = request.META.get(f'HTTP_{tenant_header.upper().replace("-", "_")}')
    if tenant_subdomain:
        tenant = get_tenant_from_domain(tenant_subdomain)
        if tenant:
            return tenant

    host = request.META.get('HTTP_HOST', '')
    if host:
        domain = host.split(':')[0]
        tenant = get_tenant_from_domain(domain)
        if tenant:
            return tenant
        if '.' in domain:
            subdomain = domain.split('.')[0]
            tenant = get_tenant_from_domain(subdomain)
            if tenant:
                return tenant

    return None


class TenantMiddleware:
    """Attach tenant to request for use in views."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = get_current_tenant(request)
        return self.get_response(request)
