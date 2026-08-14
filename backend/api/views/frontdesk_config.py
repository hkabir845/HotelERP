"""Frontdesk master data, rate schedule, and availability forecasts."""
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    BedInfo,
    BoardType,
    BookingAgent,
    CancellationRule,
    Company,
    ComplimentaryOption,
    ExtraChargeGroup,
    ExtraChargeItem,
    GuestSource,
    Package,
    RatePlan,
    Reservation,
    ReservationStatus,
    Room,
    RoomFacility,
    RoomGroup,
    RoomStatusEnum,
    RoomType,
    RoomTypeSpecialRate,
    RoomViewType,
)
from api.views import deny_if_no_tenant

BLOCKING_ROOM = {RoomStatusEnum.OUT_OF_ORDER, RoomStatusEnum.MAINTENANCE}
BUSY_RES = {
    ReservationStatus.PENDING,
    ReservationStatus.CONFIRMED,
    ReservationStatus.CHECKED_IN,
}

SIMPLE_KINDS = {
    'packages': Package,
    'room-view-types': RoomViewType,
    'bed-info': BedInfo,
    'room-facilities': RoomFacility,
    'room-groups': RoomGroup,
    'extra-charge-groups': ExtraChargeGroup,
    'rate-plans': RatePlan,
    'complimentary-options': ComplimentaryOption,
    'guest-sources': GuestSource,
}


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _dec(value, default='0'):
    if value in (None, ''):
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _int(value, default=0):
    if value in (None, ''):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value in (None, ''):
        return default
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def _date(value):
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs):
    return [{'id': row.id, 'name': getattr(row, 'name', str(row.id))} for row in qs]


def _options(tenant):
    return {
        'room_types': _opt(RoomType.objects.filter(tenant=tenant).order_by('name')),
        'rate_plans': _opt(RatePlan.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'extra_charge_groups': _opt(ExtraChargeGroup.objects.filter(tenant=tenant).order_by('name')),
        'room_groups': _opt(RoomGroup.objects.filter(tenant=tenant).order_by('name')),
        'room_view_types': _opt(RoomViewType.objects.filter(tenant=tenant).order_by('name')),
        'bed_info': _opt(BedInfo.objects.filter(tenant=tenant).order_by('name')),
        'board_types': _opt(BoardType.objects.filter(tenant=tenant).order_by('name')),
    }


def serialize_simple(row):
    data = {
        'id': row.id,
        'name': row.name,
        'description': getattr(row, 'description', None) or '',
        'is_active': getattr(row, 'is_active', True),
    }
    if hasattr(row, 'price'):
        data['price'] = float(row.price or 0)
    if hasattr(row, 'icon'):
        data['icon'] = row.icon or ''
    return data


def serialize_room_type(row):
    return {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'max_occupancy': row.max_occupancy,
        'extra_occupancy': row.extra_occupancy,
        'base_rate': float(row.base_rate or 0),
        'extra_bed_rate': float(row.extra_bed_rate) if row.extra_bed_rate is not None else None,
        'amenities': row.amenities or '',
        'is_active': row.is_active,
        'room_count': getattr(row, 'room_count_anno', row.rooms.count()),
    }


def serialize_room(row):
    return {
        'id': row.id,
        'room_number': row.room_number,
        'room_type_id': row.room_type_id,
        'room_type_name': row.room_type.name if row.room_type_id else '',
        'floor': row.floor,
        'status': row.status,
        'bed_type': row.bed_type or '',
        'view': row.view or '',
        'smoking_allowed': row.smoking_allowed,
        'rack_rate': float(row.rack_rate) if row.rack_rate is not None else None,
        'notes': row.notes or '',
        'is_active': row.is_active,
    }


def serialize_extra_item(row):
    return {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'amount': float(row.amount or 0),
        'group_id': row.group_id,
        'group_name': row.group.name if row.group_id else '',
        'is_active': row.is_active,
    }


def serialize_agent(row):
    return {
        'id': row.id,
        'name': row.name,
        'contact_person': row.contact_person or '',
        'email': row.email or '',
        'phone': row.phone or '',
        'commission_rate': float(row.commission_rate) if row.commission_rate is not None else None,
        'is_active': row.is_active,
    }


def serialize_company(row):
    return {
        'id': row.id,
        'name': row.name,
        'contact_person': row.contact_person or '',
        'email': row.email or '',
        'phone': row.phone or '',
        'address': row.address or '',
        'credit_limit': float(row.credit_limit) if row.credit_limit is not None else None,
        'is_active': row.is_active,
    }


def serialize_cancel(row):
    return {
        'id': row.id,
        'name': row.name,
        'hours_before_checkin': row.hours_before_checkin,
        'cancellation_charge_percentage': (
            float(row.cancellation_charge_percentage)
            if row.cancellation_charge_percentage is not None
            else None
        ),
        'cancellation_charge_amount': (
            float(row.cancellation_charge_amount)
            if row.cancellation_charge_amount is not None
            else None
        ),
        'is_active': row.is_active,
    }


def serialize_board(row):
    return {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'additional_charge': float(row.additional_charge or 0),
        'is_active': row.is_active,
    }


def serialize_special(row):
    return {
        'id': row.id,
        'room_type_id': row.room_type_id,
        'room_type_name': row.room_type.name if row.room_type_id else '',
        'rate_plan_id': row.rate_plan_id,
        'rate_plan_name': row.rate_plan.name if row.rate_plan_id else '',
        'start_date': row.start_date.isoformat() if row.start_date else None,
        'end_date': row.end_date.isoformat() if row.end_date else None,
        'rate': float(row.rate or 0),
        'notes': row.notes or '',
        'is_active': row.is_active,
    }


def _list_qs(kind, tenant):
    if kind in SIMPLE_KINDS:
        return SIMPLE_KINDS[kind].objects.filter(tenant=tenant).order_by('name')
    if kind == 'room-types':
        return RoomType.objects.filter(tenant=tenant).annotate(room_count_anno=Count('rooms')).order_by('name')
    if kind == 'rooms':
        return Room.objects.select_related('room_type').filter(tenant=tenant).order_by('floor', 'room_number')
    if kind == 'extra-charge-items':
        return ExtraChargeItem.objects.select_related('group').filter(tenant=tenant).order_by('name')
    if kind == 'booking-agents':
        return BookingAgent.objects.filter(tenant=tenant).order_by('name')
    if kind == 'companies':
        return Company.objects.filter(tenant=tenant).order_by('name')
    if kind == 'cancellation-rules':
        return CancellationRule.objects.filter(tenant=tenant).order_by('name')
    if kind == 'board-types':
        return BoardType.objects.filter(tenant=tenant).order_by('name')
    if kind == 'room-type-special-rates':
        return (
            RoomTypeSpecialRate.objects.select_related('room_type', 'rate_plan')
            .filter(tenant=tenant)
            .order_by('-start_date', 'room_type__name')
        )
    return None


def serialize_kind(kind, row):
    if kind in SIMPLE_KINDS:
        return serialize_simple(row)
    return {
        'room-types': serialize_room_type,
        'rooms': serialize_room,
        'extra-charge-items': serialize_extra_item,
        'booking-agents': serialize_agent,
        'companies': serialize_company,
        'cancellation-rules': serialize_cancel,
        'board-types': serialize_board,
        'room-type-special-rates': serialize_special,
    }[kind](row)


def _create_or_update(kind, tenant, data, instance=None):
    name = (data.get('name') or '').strip()

    if kind in SIMPLE_KINDS:
        if not name:
            raise ValueError('Name is required')
        model = SIMPLE_KINDS[kind]
        kwargs = {
            'name': name,
            'description': data.get('description') or '',
            'is_active': _bool(data.get('is_active'), True),
        }
        if kind == 'packages':
            kwargs['price'] = _dec(data.get('price') or data.get('amount'))
        if kind == 'room-facilities':
            kwargs['icon'] = data.get('icon') or ''
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return model.objects.create(tenant=tenant, **kwargs)

    if kind == 'room-types':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'description': data.get('description') or '',
            'max_occupancy': _int(data.get('max_occupancy'), 2),
            'extra_occupancy': _int(data.get('extra_occupancy'), 0),
            'base_rate': _dec(data.get('base_rate') or data.get('amount')),
            'extra_bed_rate': _dec(data.get('extra_bed_rate')) if data.get('extra_bed_rate') not in (None, '') else None,
            'amenities': data.get('amenities') or '',
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return RoomType.objects.create(tenant=tenant, **kwargs)

    if kind == 'rooms':
        room_number = (data.get('room_number') or name or '').strip()
        if not room_number:
            raise ValueError('Room number is required')
        room_type = _fk(RoomType, tenant, data.get('room_type_id'))
        if not room_type and instance:
            room_type = instance.room_type
        if not room_type:
            raise ValueError('Room type is required')
        kwargs = {
            'room_number': room_number,
            'room_type': room_type,
            'floor': _int(data.get('floor'), None) if data.get('floor') not in (None, '') else None,
            'status': data.get('status') or RoomStatusEnum.AVAILABLE,
            'bed_type': data.get('bed_type') or '',
            'view': data.get('view') or '',
            'smoking_allowed': _bool(data.get('smoking_allowed'), False),
            'rack_rate': _dec(data.get('rack_rate')) if data.get('rack_rate') not in (None, '') else None,
            'notes': data.get('notes') or '',
            'is_active': _bool(data.get('is_active'), True),
        }
        if kwargs['floor'] is None and data.get('floor') in (None, ''):
            kwargs['floor'] = instance.floor if instance else None
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return Room.objects.create(tenant=tenant, **kwargs)

    if kind == 'extra-charge-items':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'description': data.get('description') or '',
            'amount': _dec(data.get('amount')),
            'group': _fk(ExtraChargeGroup, tenant, data.get('group_id')),
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return ExtraChargeItem.objects.create(tenant=tenant, **kwargs)

    if kind == 'booking-agents':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'contact_person': data.get('contact_person') or '',
            'email': data.get('email') or '',
            'phone': data.get('phone') or '',
            'commission_rate': _dec(data.get('commission_rate')) if data.get('commission_rate') not in (None, '') else None,
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return BookingAgent.objects.create(tenant=tenant, **kwargs)

    if kind == 'companies':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'contact_person': data.get('contact_person') or '',
            'email': data.get('email') or '',
            'phone': data.get('phone') or '',
            'address': data.get('address') or '',
            'credit_limit': _dec(data.get('credit_limit')) if data.get('credit_limit') not in (None, '') else None,
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return Company.objects.create(tenant=tenant, **kwargs)

    if kind == 'cancellation-rules':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'hours_before_checkin': _int(data.get('hours_before_checkin'), None)
            if data.get('hours_before_checkin') not in (None, '')
            else None,
            'cancellation_charge_percentage': (
                _dec(data.get('cancellation_charge_percentage'))
                if data.get('cancellation_charge_percentage') not in (None, '')
                else None
            ),
            'cancellation_charge_amount': (
                _dec(data.get('cancellation_charge_amount'))
                if data.get('cancellation_charge_amount') not in (None, '')
                else None
            ),
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return CancellationRule.objects.create(tenant=tenant, **kwargs)

    if kind == 'board-types':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'description': data.get('description') or '',
            'additional_charge': _dec(data.get('additional_charge') or data.get('amount')),
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return BoardType.objects.create(tenant=tenant, **kwargs)

    if kind == 'room-type-special-rates':
        room_type = _fk(RoomType, tenant, data.get('room_type_id'))
        if instance and not room_type:
            room_type = instance.room_type
        if not room_type:
            raise ValueError('Room type is required')
        start = _date(data.get('start_date'))
        end = _date(data.get('end_date'))
        if not start or not end:
            raise ValueError('Start and end dates are required')
        if end < start:
            raise ValueError('End date must be on or after start date')
        kwargs = {
            'room_type': room_type,
            'rate_plan': _fk(RatePlan, tenant, data.get('rate_plan_id')),
            'start_date': start,
            'end_date': end,
            'rate': _dec(data.get('rate') or data.get('amount')),
            'notes': data.get('notes') or '',
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return RoomTypeSpecialRate.objects.create(tenant=tenant, **kwargs)

    raise ValueError(f'Unknown kind: {kind}')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    qs = _list_qs(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        try:
            row = _create_or_update(kind, tenant, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_kind(kind, row), status=status.HTTP_201_CREATED)
    search = (request.query_params.get('search') or '').strip()
    if search:
        if hasattr(qs.model, 'name'):
            qs = qs.filter(Q(name__icontains=search))
        elif hasattr(qs.model, 'room_number'):
            qs = qs.filter(Q(room_number__icontains=search))
        elif kind == 'room-type-special-rates':
            qs = qs.filter(Q(room_type__name__icontains=search) | Q(notes__icontains=search))
    items = [serialize_kind(kind, row) for row in qs[:500]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    qs = _list_qs(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        row = qs.get(id=pk)
    except qs.model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _create_or_update(kind, tenant, request.data or {}, instance=row)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_kind(kind, row))
    return Response(serialize_kind(kind, row))


def _range(request, default_days=13):
    start = _date(request.query_params.get('from')) or date.today()
    end = _date(request.query_params.get('to'))
    if not end:
        end = start + timedelta(days=default_days)
    if end < start:
        start, end = end, start
    if (end - start).days > 62:
        end = start + timedelta(days=62)
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)
    return start, end, days


def _busy_room_ids(tenant, day):
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())
    return set(
        Reservation.objects.filter(
            tenant=tenant,
            status__in=BUSY_RES,
            room_id__isnull=False,
            check_in_date__lte=end,
            check_out_date__gt=start,
        ).values_list('room_id', flat=True)
    )


def _rate_for(room_type, day, specials, rate_plan_id=None):
    matches = [
        row
        for row in specials
        if row.room_type_id == room_type.id
        and row.is_active
        and row.start_date <= day <= row.end_date
        and (not rate_plan_id or row.rate_plan_id == int(rate_plan_id) or row.rate_plan_id is None)
    ]
    if rate_plan_id:
        planned = [row for row in matches if row.rate_plan_id == int(rate_plan_id)]
        if planned:
            matches = planned
    if not matches:
        return float(room_type.base_rate or 0), False
    matches.sort(key=lambda row: (row.rate_plan_id is None, row.start_date), reverse=True)
    return float(matches[0].rate or 0), True


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rate_schedule(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    start, end, days = _range(request)
    plan_id = request.query_params.get('rate_plan_id') or None
    types = list(RoomType.objects.filter(tenant=tenant, is_active=True).order_by('name'))
    specials = list(
        RoomTypeSpecialRate.objects.filter(
            tenant=tenant,
            is_active=True,
            start_date__lte=end,
            end_date__gte=start,
        )
    )
    rows = []
    for rt in types:
        cells = []
        for day in days:
            rate, special = _rate_for(rt, day, specials, plan_id)
            cells.append({'date': day.isoformat(), 'rate': rate, 'special': special})
        rows.append({
            'room_type_id': rt.id,
            'room_type': rt.name,
            'base_rate': float(rt.base_rate or 0),
            'cells': cells,
        })
    return Response({
        'from': start.isoformat(),
        'to': end.isoformat(),
        'dates': [d.isoformat() for d in days],
        'rows': rows,
        'options': {'rate_plans': _options(tenant)['rate_plans']},
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def forecast_room_type(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    start, end, days = _range(request)
    types = list(RoomType.objects.filter(tenant=tenant, is_active=True).order_by('name'))
    rooms = list(Room.objects.filter(tenant=tenant, is_active=True).select_related('room_type'))
    busy_by_day = {day: _busy_room_ids(tenant, day) for day in days}
    rows = []
    for rt in types:
        typed = [room for room in rooms if room.room_type_id == rt.id]
        total = len(typed)
        cells = []
        for day in days:
            busy = busy_by_day[day]
            occupied = sum(1 for room in typed if room.id in busy)
            blocked = sum(1 for room in typed if room.status in BLOCKING_ROOM and room.id not in busy)
            available = max(0, total - occupied - blocked)
            cells.append({
                'date': day.isoformat(),
                'total': total,
                'occupied': occupied,
                'blocked': blocked,
                'available': available,
            })
        rows.append({'room_type_id': rt.id, 'room_type': rt.name, 'total': total, 'cells': cells})
    return Response({
        'from': start.isoformat(),
        'to': end.isoformat(),
        'dates': [d.isoformat() for d in days],
        'rows': rows,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def forecast_availability(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    start, end, days = _range(request, default_days=9)
    rooms = list(
        Room.objects.select_related('room_type')
        .filter(tenant=tenant, is_active=True)
        .order_by('floor', 'room_number')
    )
    busy_by_day = {day: _busy_room_ids(tenant, day) for day in days}
    rows = []
    for room in rooms:
        cells = []
        for day in days:
            busy = room.id in busy_by_day[day]
            if busy:
                state = 'occupied'
            elif room.status in BLOCKING_ROOM:
                state = 'blocked'
            else:
                state = 'available'
            cells.append({'date': day.isoformat(), 'state': state})
        rows.append({
            'room_id': room.id,
            'room_number': room.room_number,
            'room_type': room.room_type.name if room.room_type_id else '',
            'floor': room.floor,
            'cells': cells,
        })
    return Response({
        'from': start.isoformat(),
        'to': end.isoformat(),
        'dates': [d.isoformat() for d in days],
        'rows': rows,
    })
