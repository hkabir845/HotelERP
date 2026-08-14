"""Shared helpers for API views."""
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


def deny_if_no_tenant(user, detail='Access denied'):
    """Return 403 response if user has no tenant and is not superuser."""
    if not user.tenant_id and not user.is_superuser:
        return Response({'detail': detail}, status=status.HTTP_403_FORBIDDEN)
    return None


def deny_if_lacks_capability(user, capability: str, detail='Insufficient permissions'):
    """Return 403 if the user's role lacks a named capability."""
    from api.rbac import has_capability
    if has_capability(getattr(user, 'role', None), capability, is_superuser=bool(user.is_superuser)):
        return None
    return Response({'detail': detail}, status=status.HTTP_403_FORBIDDEN)


def deny_if_lacks_module(user, module_key: str, detail='Module not available for your role'):
    """Return 403 if effective RBAC modules do not include module_key."""
    from api.rbac import effective_modules
    if user.is_superuser:
        return None
    tenant = getattr(user, 'tenant', None)
    tenant_mods = tenant.get_enabled_modules() if tenant is not None else []
    if not tenant and user.tenant_id:
        from api.models import Tenant
        tenant = Tenant.objects.filter(id=user.tenant_id).first()
        tenant_mods = tenant.get_enabled_modules() if tenant else []
    mods = effective_modules(getattr(user, 'role', None), tenant_mods, is_superuser=False)
    role = (getattr(user, 'role', None) or '').lower()
    if role in ('admin', 'superadmin'):
        return None
    if module_key in mods:
        return None
    return Response({'detail': detail}, status=status.HTTP_403_FORBIDDEN)

def serialize_user(user):
    """Serialize user including tenant SaaS context and RBAC effective access."""
    from api.rbac import serialize_rbac

    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role,
        'tenant_id': user.tenant_id,
        'is_active': user.is_active,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'avatar': user.avatar,
        'department': user.department,
        'designation': user.designation,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'tenant': None,
        'product_type': None,
        'enabled_modules': [],
    }
    tenant = getattr(user, 'tenant', None)
    tenant_modules = []
    if tenant is not None:
        expired = bool(
            tenant.subscription_expires_at and tenant.subscription_expires_at < timezone.now()
        )
        tenant_modules = tenant.get_enabled_modules()
        payload['tenant'] = {
            'id': tenant.id,
            'name': tenant.name,
            'subdomain': tenant.subdomain,
            'logo': tenant.logo,
            'product_type': tenant.product_type,
            'enabled_modules': tenant_modules,
            'landing_enabled': tenant.landing_enabled,
            'is_active': tenant.is_active,
            'subscription_plan': tenant.subscription_plan,
            'subscription_expires_at': (
                tenant.subscription_expires_at.isoformat() if tenant.subscription_expires_at else None
            ),
            'subscription_active': not expired,
        }
        payload['product_type'] = tenant.product_type
    elif user.is_superuser:
        from api.models.tenant import ALL_MODULES
        tenant_modules = list(ALL_MODULES)
        payload['product_type'] = 'saas'

    rbac = serialize_rbac(user)
    # Effective modules = tenant ∩ role (admins keep full tenant set)
    payload['enabled_modules'] = rbac['modules']
    payload['rbac'] = rbac
    payload['role_label'] = rbac['role_label']
    payload['home_path'] = rbac['home_path']
    payload['capabilities'] = rbac['capabilities']
    return payload
