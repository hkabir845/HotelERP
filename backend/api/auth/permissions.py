"""DRF permission: authenticated + role/module RBAC for API path prefixes."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated

from api.rbac import effective_modules

# Longest-prefix wins. Unlisted /api/* paths stay authenticated-only.
_PATH_MODULE = (
    ('/api/accounts/', 'accounts'),
    ('/api/inventory/', 'inventory'),
    ('/api/fnb/', 'fnb'),
    ('/api/housekeeping/', 'housekeeping'),
    ('/api/frontdesk/', 'frontdesk'),
    ('/api/reservations/', 'frontdesk'),
    ('/api/guests', 'frontdesk'),
    ('/api/banquet/', 'banquet'),
    ('/api/hr/', 'hr'),
    ('/api/crm/', 'crm'),
    ('/api/assets/', 'assets'),
    ('/api/broadcast/', 'broadcast'),
    ('/api/utilities/', 'utilities'),
    ('/api/website/', 'utilities'),
    ('/api/reports/', 'reports'),
    ('/api/channels', 'channel'),
    ('/api/services', 'spa'),
    ('/api/ops', 'assets'),
)

_SKIP_PREFIXES = (
    '/api/auth/',
    '/api/public/',
    '/api/core/',
    '/api/superadmin/',
    '/api/config',
    '/api/catalog',
)


def module_for_path(path: str) -> str | None:
    path = (path or '').split('?')[0]
    for prefix in _SKIP_PREFIXES:
        if path.startswith(prefix) or path == prefix.rstrip('/'):
            return None
    for prefix, module in _PATH_MODULE:
        if path.startswith(prefix):
            return module
    return None


def user_may_access_module(user, module_key: str) -> bool:
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    role = (getattr(user, 'role', None) or '').lower()
    if role in ('admin', 'superadmin'):
        return True
    tenant = getattr(user, 'tenant', None)
    if tenant is None and getattr(user, 'tenant_id', None):
        from api.models import Tenant
        tenant = Tenant.objects.filter(id=user.tenant_id).first()
    tenant_mods = tenant.get_enabled_modules() if tenant is not None else []
    mods = effective_modules(role, tenant_mods, is_superuser=False)
    return module_key in mods


class IsAuthenticatedWithModule(IsAuthenticated):
    """
    Drop-in replacement for IsAuthenticated that also enforces
    role ∩ tenant module access for mapped API prefixes.
    """

    message = 'You do not have access to this module for your role.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        module = module_for_path(request.path)
        if not module:
            return True
        return user_may_access_module(request.user, module)
