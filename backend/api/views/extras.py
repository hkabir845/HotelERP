"""Laundry, spa, hall, pool, travel desk, channel manager, HR."""
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import ChannelMapping, Employee, ServiceBooking
from api.views import deny_if_no_tenant


def _tenant(request):
    return getattr(request.user, 'tenant', None) or getattr(request, 'tenant', None)


def _serialize_booking(row):
    open_status = row.status in ('open', 'pending', '')
    return {
        'id': row.id,
        'kind': row.kind,
        'reference': row.reference,
        'guest_name': row.guest_name,
        'room_number': row.room_number,
        'item': row.item,
        'quantity': float(row.quantity or 0),
        'amount': float(row.amount or 0),
        'status': row.status,
        'scheduled_at': row.scheduled_at.isoformat() if row.scheduled_at else None,
        'notes': row.notes,
        'created_at': row.created_at.isoformat() if row.created_at else None,
        'can_complete': open_status,
        'can_cancel': open_status,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def service_bookings(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    kind = request.query_params.get('kind') or request.data.get('kind')
    if request.method == 'POST':
        data = request.data or {}
        kind = (data.get('kind') or kind or '').strip()
        if kind not in dict(ServiceBooking.KIND_CHOICES):
            return Response({'detail': 'Invalid kind'}, status=status.HTTP_400_BAD_REQUEST)
        count = ServiceBooking.objects.filter(tenant=tenant, kind=kind).count() + 1
        row = ServiceBooking.objects.create(
            tenant=tenant,
            kind=kind,
            reference=data.get('reference') or f'{kind[:3].upper()}-{count:05d}',
            guest_name=data.get('guest_name') or '',
            room_number=data.get('room_number') or '',
            item=data.get('item') or '',
            quantity=data.get('quantity') or 1,
            amount=data.get('amount') or 0,
            status=data.get('status') or 'open',
            notes=data.get('notes') or '',
        )
        return Response(_serialize_booking(row), status=status.HTTP_201_CREATED)
    qs = ServiceBooking.objects.filter(tenant=tenant)
    if kind:
        qs = qs.filter(kind=kind)
    return Response({'items': [_serialize_booking(r) for r in qs[:200]]})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def service_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    row = ServiceBooking.objects.filter(tenant=tenant, id=pk).first()
    if not row:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    action = (request.data or {}).get('action')
    if action == 'complete':
        row.status = 'completed'
    elif action == 'cancel':
        row.status = 'cancelled'
    else:
        return Response({'detail': 'Unknown action'}, status=status.HTTP_400_BAD_REQUEST)
    row.save(update_fields=['status'])
    return Response(_serialize_booking(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def channels(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        data = request.data or {}
        row = ChannelMapping.objects.create(
            tenant=tenant,
            channel_name=(data.get('channel_name') or '').strip() or 'OTA',
            property_code=data.get('property_code') or '',
            is_active=bool(data.get('is_active', True)),
            notes=data.get('notes') or '',
        )
        return Response({
            'id': row.id,
            'channel_name': row.channel_name,
            'property_code': row.property_code,
            'is_active': row.is_active,
            'notes': row.notes,
        }, status=status.HTTP_201_CREATED)
    rows = ChannelMapping.objects.filter(tenant=tenant)
    return Response({
        'items': [
            {
                'id': r.id,
                'channel_name': r.channel_name,
                'property_code': r.property_code,
                'is_active': r.is_active,
                'notes': r.notes,
            }
            for r in rows
        ]
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def employees(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        data = request.data or {}
        first = (data.get('first_name') or '').strip()
        last = (data.get('last_name') or '').strip()
        if not first:
            return Response({'detail': 'first_name is required'}, status=status.HTTP_400_BAD_REQUEST)
        count = Employee.objects.filter(tenant=tenant).count() + 1
        row = Employee.objects.create(
            tenant=tenant,
            employee_number=data.get('employee_number') or f'EMP-{count:05d}',
            first_name=first,
            last_name=last or '-',
            email=data.get('email') or None,
            phone=data.get('phone') or None,
            department=data.get('department') or None,
            designation=data.get('designation') or None,
            hire_date=data.get('hire_date') or timezone.now().date(),
            salary=data.get('salary') or data.get('amount') or None,
        )
        return Response({
            'id': row.id,
            'employee_number': row.employee_number,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'email': row.email,
            'phone': row.phone,
            'department': row.department,
            'designation': row.designation,
            'salary': float(row.salary or 0),
            'status': row.status,
        }, status=status.HTTP_201_CREATED)
    rows = Employee.objects.filter(tenant=tenant)
    return Response({
        'items': [
            {
                'id': r.id,
                'employee_number': r.employee_number,
                'first_name': r.first_name,
                'last_name': r.last_name,
                'email': r.email,
                'phone': r.phone,
                'department': r.department,
                'designation': r.designation,
                'salary': float(r.salary or 0),
                'status': r.status,
            }
            for r in rows[:200]
        ]
    })


def _serialize_catalog(row):
    return {
        'id': row.id,
        'kind': row.kind,
        'name': row.name,
        'code': row.code,
        'amount': float(row.amount or 0),
        'status': row.status,
        'notes': row.notes,
        'created_at': row.created_at.isoformat() if row.created_at else None,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def catalog(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    kind = (request.query_params.get('kind') or request.data.get('kind') or '').strip()
    if request.method == 'POST':
        data = request.data or {}
        kind = (data.get('kind') or kind).strip()
        if not kind:
            return Response({'detail': 'kind is required'}, status=status.HTTP_400_BAD_REQUEST)
        name = (data.get('name') or data.get('title') or data.get('item') or '').strip()
        if not name:
            return Response({'detail': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
        from api.models import CatalogRecord
        row = CatalogRecord.objects.create(
            tenant=tenant,
            kind=kind,
            name=name,
            code=data.get('code') or '',
            amount=data.get('amount') or 0,
            status=data.get('status') or 'active',
            notes=data.get('notes') or '',
        )
        return Response(_serialize_catalog(row), status=status.HTTP_201_CREATED)
    from api.models import CatalogRecord
    qs = CatalogRecord.objects.filter(tenant=tenant)
    if kind:
        qs = qs.filter(kind=kind)
    return Response({'items': [_serialize_catalog(r) for r in qs[:300]]})
