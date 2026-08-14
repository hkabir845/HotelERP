"""Authentication endpoints."""
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.auth.jwt_utils import (
    authenticate_user,
    build_token_data,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from api.models import Tenant
from api.views import serialize_user

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint."""
    login_data = request.data
    username = (login_data.get('username') or '').strip()
    password = login_data.get('password') or ''
    tenant_subdomain = (login_data.get('tenant_subdomain') or '').strip() or None

    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tenant_id = None
    if tenant_subdomain:
        tenant = Tenant.objects.filter(subdomain=tenant_subdomain, is_active=True).first()
        if not tenant:
            return Response(
                {'detail': 'Tenant not found or inactive'},
                status=status.HTTP_404_NOT_FOUND,
            )
        tenant_id = tenant.id

    user = authenticate_user(username=username, password=password, tenant_id=tenant_id)
    if not user:
        return Response(
            {'detail': 'Incorrect username or password'},
            status=status.HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Enforce subscription for tenant users (superadmin always allowed)
    if not user.is_superuser:
        user_tenant = None
        if user.tenant_id:
            user_tenant = Tenant.objects.filter(id=user.tenant_id).first()
        elif tenant_subdomain:
            user_tenant = Tenant.objects.filter(subdomain=tenant_subdomain).first()
        if user_tenant and user_tenant.subscription_expires_at:
            if user_tenant.subscription_expires_at < timezone.now():
                return Response(
                    {
                        'detail': 'Subscription expired. Contact your platform administrator to renew.',
                        'code': 'subscription_expired',
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
        if user_tenant and not user_tenant.is_active:
            return Response(
                {'detail': 'This business account is inactive.'},
                status=status.HTTP_403_FORBIDDEN,
            )

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    token_data = build_token_data(user)
    return Response({
        'access_token': create_access_token(data=token_data),
        'refresh_token': create_refresh_token(data=token_data),
        'token_type': 'bearer',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token using refresh token."""
    refresh_token_value = request.data.get('refresh_token')
    if not refresh_token_value:
        return Response(
            {'detail': 'refresh_token is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = decode_token(refresh_token_value)
    if not payload or payload.get('type') != 'refresh':
        return Response(
            {'detail': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    username = payload.get('sub')
    if not username:
        return Response(
            {'detail': 'Invalid token payload'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = User.objects.filter(username=username).first()
    if not user or not user.is_active:
        return Response(
            {'detail': 'User not found or inactive'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token_data = build_token_data(user)
    return Response({
        'access_token': create_access_token(data=token_data),
        'refresh_token': create_refresh_token(data=token_data),
        'token_type': 'bearer',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user information with tenant SaaS context."""
    user = request.user
    # Ensure tenant relation is available for serialize_user
    if getattr(user, 'tenant_id', None) and not getattr(user, '_tenant_cache_ready', False):
        try:
            from api.models import Tenant
            user.tenant = Tenant.objects.filter(id=user.tenant_id).first()
        except Exception:
            pass
    return Response(serialize_user(user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register(request):
    """Register a new user (superuser or admin only)."""
    current_user = request.user
    user_data = request.data

    if not current_user.is_superuser:
        from api.rbac import has_capability, CAP_MANAGE_USERS
        if current_user.role != 'admin' and not has_capability(current_user.role, CAP_MANAGE_USERS):
            return Response(
                {'detail': 'Not enough permissions to create users'},
                status=status.HTTP_403_FORBIDDEN,
            )

    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.get('password')

    if not username or not email or not password:
        return Response(
            {'detail': 'username, email, and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_user = User.objects.filter(
        Q(username=username) | Q(email=email)
    ).first()
    if existing_user:
        return Response(
            {'detail': 'Username or email already registered'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tenant_id = user_data.get('tenant_id') or current_user.tenant_id
    tenant = Tenant.objects.filter(id=tenant_id).first() if tenant_id else None

    new_user = User(
        username=username,
        email=email,
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        phone=user_data.get('phone'),
        role=user_data.get('role') or 'staff',
        tenant=tenant,
        is_active=True,
        is_superuser=False,
        is_staff=True,
    )
    new_user.password = get_password_hash(password)
    new_user.save()

    return Response(serialize_user(new_user))


@api_view(['GET'])
@permission_classes([AllowAny])
def roles_catalog(request):
    """Public catalog of operational hotel roles (for login demos / docs)."""
    from api.rbac import list_operational_roles
    return Response({'roles': list_operational_roles()})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_access(request):
    """Current user's effective RBAC snapshot."""
    from api.rbac import serialize_rbac
    user = request.user
    if getattr(user, 'tenant_id', None):
        from api.models import Tenant
        user.tenant = Tenant.objects.filter(id=user.tenant_id).first()
    return Response(serialize_rbac(user))
