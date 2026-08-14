"""Utilities endpoints."""
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.rbac import has_capability, CAP_MANAGE_USERS, list_operational_roles
from api.views import deny_if_no_tenant

User = get_user_model()


def _can_manage_users(user):
    if getattr(user, 'is_superuser', False):
        return True
    role = (getattr(user, 'role', None) or '').lower()
    return role == 'admin' or has_capability(role, CAP_MANAGE_USERS)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def settings_view(request):
    """Get or update system settings."""
    if request.method == 'PUT':
        current_user = request.user
        if not _can_manage_users(current_user) and not current_user.is_superuser:
            role = (getattr(current_user, 'role', None) or '').lower()
            if role != 'admin':
                return Response(
                    {'detail': 'Access denied. Admin only.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        allowed_fields = {
            'hotel_name', 'currency', 'timezone', 'date_format',
            'email_enabled', 'sms_enabled', 'notification_enabled',
        }
        updated = {
            key: value for key, value in request.data.items()
            if key in allowed_fields and value is not None
        }

        return Response({
            'message': 'Settings updated successfully',
            'settings': updated,
        })

    settings_data = {
        'hotel_name': 'Hotel ERP',
        'currency': 'BDT',
        'timezone': 'Asia/Dhaka',
        'date_format': 'YYYY-MM-DD',
        'email_enabled': True,
        'sms_enabled': False,
        'notification_enabled': True,
    }
    return Response({'settings': settings_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    """List users for the property (admin) or all users (superuser)."""
    current_user = request.user
    if not _can_manage_users(current_user):
        return Response(
            {'detail': 'Access denied. Admin only.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    search = request.query_params.get('search')
    qs = User.objects.all()
    if not current_user.is_superuser:
        denied = deny_if_no_tenant(current_user)
        if denied:
            return denied
        qs = qs.filter(tenant_id=current_user.tenant_id)

    if search:
        qs = qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(username__icontains=search)
        )

    result = []
    for user in qs.order_by('username')[:500]:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'role': user.role,
            'department': user.department,
            'designation': user.designation,
            'tenant_id': user.tenant_id,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        })

    return Response({
        'users': result,
        'role_options': list_operational_roles(),
    })
