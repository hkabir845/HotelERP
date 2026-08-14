"""Tenant website CMS — gallery, blog, bookings, contact inbox."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Order, Reservation, Tenant, WebsiteContact
from api.views.public import _find_tenant, _tenant_ok


def _staff_tenant(request):
    tenant = getattr(request.user, 'tenant', None) or getattr(request, 'tenant', None)
    if not tenant and request.user.is_superuser:
        subdomain = request.query_params.get('subdomain') or request.data.get('subdomain')
        if subdomain:
            tenant = Tenant.objects.filter(subdomain=subdomain.lower()).first()
    return tenant


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def website_content(request):
    tenant = _staff_tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    if not tenant.has_module('landing'):
        return Response({'detail': 'Website module is not enabled'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        payload = request.data.get('landing_content', request.data)
        tenant.set_landing_content(payload)
        tenant.save(update_fields=['landing_content'])
    return Response({'landing_content': tenant.get_landing_content(), 'subdomain': tenant.subdomain})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def website_contacts(request):
    tenant = _staff_tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    rows = WebsiteContact.objects.filter(tenant=tenant)[:100]
    return Response({
        'contacts': [
            {
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'subject': c.subject,
                'message': c.message,
                'status': c.status,
                'created_at': c.created_at.isoformat() if c.created_at else None,
            }
            for c in rows
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def website_bookings(request):
    tenant = _staff_tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    bookings = list(
        Reservation.objects.filter(tenant=tenant, source='website')
        .order_by('-created_at')[:50]
        .values('id', 'reservation_number', 'status', 'check_in_date', 'check_out_date', 'total_amount', 'created_at')
    )
    orders = list(
        Order.objects.filter(tenant=tenant, source='website')
        .order_by('-created_at')[:50]
        .values('id', 'order_number', 'status', 'payment_status', 'total_amount', 'created_at')
    )
    return Response({'bookings': bookings, 'orders': orders})


@api_view(['POST'])
@permission_classes([AllowAny])
def public_contact(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.landing_enabled or not tenant.has_module('landing'):
        return Response({'detail': 'Website disabled'}, status=status.HTTP_404_NOT_FOUND)
    data = request.data or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()
    if not name or not email or not message:
        return Response({'detail': 'Name, email, and message are required'}, status=status.HTTP_400_BAD_REQUEST)
    row = WebsiteContact.objects.create(
        tenant=tenant,
        name=name[:200],
        email=email[:255],
        phone=(data.get('phone') or '')[:50],
        subject=(data.get('subject') or 'Website inquiry')[:255],
        message=message,
    )
    return Response({'id': row.id, 'message': 'Thank you. We will contact you soon.'}, status=status.HTTP_201_CREATED)
