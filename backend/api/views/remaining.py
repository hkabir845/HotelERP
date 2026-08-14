"""Leftover GYOROOM screens: agent funds, HK extras, assets masters, broadcast, utilities."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    AgentFundRequest,
    AmenityDistribution,
    AmenityDistributionItem,
    AssetCategory,
    AuditLog,
    BookingAgent,
    BroadcastMessage,
    Reservation,
    ReservationStatus,
    Room,
    RoomStatusEnum,
    User,
)
from api.models.asset import AssetType, AssetVendor, AssetVendorContract
from api.models.utility import (
    AcceptedPaymentMethod,
    AppRole,
    NearbyTerminal,
    PropertyImage,
    UserAccountPermission,
    UtilityBlog,
    UtilitySettings,
)
from api.views import deny_if_no_tenant


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _dec(value, default='0'):
    if value in (None, ''):
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


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


def _money(value):
    return float(value or 0)


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs):
    return [{'id': row.id, 'name': getattr(row, 'name', str(row.id))} for row in qs]


def _uname(user):
    if not user:
        return ''
    full = f'{user.first_name or ""} {user.last_name or ""}'.strip()
    return full or user.username or user.email or ''


def _settings(tenant):
    row, _ = UtilitySettings.objects.get_or_create(tenant=tenant)
    return row


def _next(model, tenant, prefix, field='request_number'):
    n = model.objects.filter(tenant=tenant).count() + 1
    return f'{prefix}-{tenant.id}-{n:05d}'


# --- Agent fund ---
def serialize_fund(row):
    return {
        'id': row.id,
        'request_number': row.request_number,
        'agent_id': row.agent_id,
        'agent_name': row.agent.name if row.agent_id else '',
        'amount': _money(row.amount),
        'request_date': row.request_date.isoformat() if row.request_date else '',
        'status': row.status,
        'notes': row.notes or '',
        'requested_by': _uname(row.requested_by),
        'can_approve': row.status == 'pending',
        'can_reject': row.status == 'pending',
        'can_pay': row.status == 'approved',
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def agent_funds(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        agent = _fk(BookingAgent, tenant, data.get('agent_id'))
        amount = _dec(data.get('amount'))
        if not agent or amount <= 0:
            return Response({'detail': 'Agent and amount are required'}, status=400)
        row = AgentFundRequest.objects.create(
            tenant=tenant,
            request_number=_next(AgentFundRequest, tenant, 'AFR'),
            agent=agent,
            amount=amount,
            request_date=_date(data.get('request_date')) or date.today(),
            notes=(data.get('notes') or '').strip() or None,
            status='pending',
            requested_by=request.user,
        )
        return Response(serialize_fund(row), status=201)
    qs = AgentFundRequest.objects.filter(tenant=tenant).select_related('agent', 'requested_by')
    items = [serialize_fund(r) for r in qs[:400]]
    return Response({
        'items': items,
        'options': {
            'agents': _opt(BookingAgent.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        },
        'summary': {'requests': len(items), 'amount': round(sum(i['amount'] for i in items), 2)},
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_fund_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = AgentFundRequest.objects.select_related('agent', 'requested_by').get(id=pk, tenant=tenant)
    except AgentFundRequest.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action == 'approve' and row.status == 'pending':
        row.status = 'approved'
        row.approved_by = request.user
        row.approved_at = timezone.now()
    elif action == 'reject' and row.status == 'pending':
        row.status = 'rejected'
        row.approved_by = request.user
        row.approved_at = timezone.now()
    elif action == 'pay' and row.status == 'approved':
        row.status = 'paid'
    else:
        return Response({'detail': f'Cannot {action} this request'}, status=400)
    row.save()
    return Response(serialize_fund(row))


# --- Housekeeping ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def guest_status_report(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    qs = (
        Reservation.objects.filter(tenant=tenant, status=ReservationStatus.CHECKED_IN)
        .select_related('guest', 'room', 'room__room_type')
        .order_by('room__room_number')
    )
    rows = []
    for res in qs:
        rows.append({
            'room': res.room.room_number if res.room_id else '',
            'type': res.room.room_type.name if res.room_id and res.room.room_type_id else '',
            'guest': res.guest.full_name if res.guest_id else '',
            'phone': (res.guest.phone or res.guest.mobile or '') if res.guest_id else '',
            'pax': (res.adults or 0) + (res.children or 0),
            'check_in': res.check_in_date.date().isoformat() if res.check_in_date else '',
            'check_out': res.check_out_date.date().isoformat() if res.check_out_date else '',
            'room_status': res.room.status if res.room_id else '',
            'due': _money(res.balance),
        })
    return Response({
        'columns': ['Room', 'Type', 'Guest', 'Phone', 'Pax', 'Check in', 'Check out', 'HK status', 'Due'],
        'rows': rows,
        'summary': {'inhouse': len(rows), 'due': round(sum(r['due'] for r in rows), 2)},
    })


def serialize_distribution(row):
    items = list(row.items.all())
    return {
        'id': row.id,
        'distribution_number': row.distribution_number,
        'room_id': row.room_id,
        'room_number': row.room.room_number if row.room_id else '',
        'distribution_date': row.distribution_date.date().isoformat() if row.distribution_date else '',
        'distributed_by': _uname(row.distributed_by),
        'notes': row.notes or '',
        'items': ', '.join(f'{i.item_name}×{i.quantity}' for i in items),
        'quantity': sum(i.quantity for i in items),
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def amenity_distributions(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        try:
            room = Room.objects.get(id=int(data.get('room_id')), tenant=tenant)
        except (Room.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'Room is required'}, status=400)
        lines = data.get('items') or []
        if not lines:
            name = (data.get('item_name') or '').strip()
            qty = int(data.get('quantity') or 1)
            if name:
                lines = [{'item_name': name, 'quantity': qty}]
        if not lines:
            return Response({'detail': 'Add at least one amenity'}, status=400)
        n = AmenityDistribution.objects.filter(tenant=tenant).count() + 1
        row = AmenityDistribution.objects.create(
            tenant=tenant,
            distribution_number=f'AMN-{tenant.id}-{n:05d}',
            room=room,
            distribution_date=timezone.now(),
            distributed_by=request.user,
            notes=(data.get('notes') or '').strip() or None,
        )
        for line in lines:
            name = (line.get('item_name') or '').strip()
            qty = int(line.get('quantity') or 0)
            if name and qty > 0:
                AmenityDistributionItem.objects.create(distribution=row, item_name=name, quantity=qty)
        return Response(serialize_distribution(row), status=201)
    qs = AmenityDistribution.objects.filter(tenant=tenant).select_related('room', 'distributed_by').prefetch_related('items')
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(Q(room__room_number__icontains=search) | Q(items__item_name__icontains=search)).distinct()
    items = [serialize_distribution(r) for r in qs[:400]]
    occupied = Room.objects.filter(tenant=tenant, is_active=True).order_by('room_number')
    return Response({
        'items': items,
        'distributions': items,
        'options': {'rooms': [{'id': r.id, 'name': r.room_number} for r in occupied]},
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def amenity_report(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    qs = AmenityDistribution.objects.filter(
        tenant=tenant,
        distribution_date__date__gte=start,
        distribution_date__date__lte=end,
    ).prefetch_related('items', 'room')
    grouped = defaultdict(lambda: {'qty': 0, 'rooms': set()})
    for row in qs:
        for item in row.items.all():
            grouped[item.item_name]['qty'] += item.quantity
            grouped[item.item_name]['rooms'].add(row.room.room_number if row.room_id else '')
    rows = [
        {'amenity': name, 'quantity': val['qty'], 'rooms': len([r for r in val['rooms'] if r])}
        for name, val in sorted(grouped.items())
    ]
    return Response({
        'columns': ['Amenity', 'Quantity', 'Rooms'],
        'rows': rows,
        'summary': {'amenities': len(rows), 'quantity': sum(r['quantity'] for r in rows)},
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def maintenance_block(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        try:
            room = Room.objects.get(id=int(data.get('room_id')), tenant=tenant)
        except (Room.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'Room is required'}, status=400)
        action = (data.get('action') or 'block').replace('-', '_')
        if action in ('block', 'maintenance'):
            room.status = RoomStatusEnum.MAINTENANCE
        elif action in ('ooo', 'out_of_order'):
            room.status = RoomStatusEnum.OUT_OF_ORDER
        elif action in ('unblock', 'release', 'available'):
            room.status = RoomStatusEnum.AVAILABLE
        else:
            return Response({'detail': f'Unknown action: {action}'}, status=400)
        note = (data.get('notes') or '').strip()
        if note:
            room.notes = ((room.notes + '\n') if room.notes else '') + note
        room.save()
        return Response({
            'id': room.id,
            'room_number': room.room_number,
            'status': room.status,
            'notes': room.notes or '',
        })
    rooms = Room.objects.filter(tenant=tenant, is_active=True).select_related('room_type').order_by('floor', 'room_number')
    items = [
        {
            'id': r.id,
            'room_number': r.room_number,
            'room_type': r.room_type.name if r.room_type_id else '',
            'floor': r.floor,
            'status': r.status,
            'notes': r.notes or '',
            'blocked': r.status in (RoomStatusEnum.MAINTENANCE, RoomStatusEnum.OUT_OF_ORDER),
        }
        for r in rooms
    ]
    return Response({
        'items': items,
        'options': {'rooms': [{'id': r['id'], 'name': r['room_number']} for r in items]},
        'summary': {
            'rooms': len(items),
            'blocked': sum(1 for r in items if r['blocked']),
        },
    })


# --- Generic named config ---
ASSET_KINDS = {
    'types': AssetType,
    'categories': AssetCategory,
    'vendors': AssetVendor,
}
UTIL_KINDS = {
    'blog': UtilityBlog,
    'images': PropertyImage,
    'terminals': NearbyTerminal,
    'payment-methods': AcceptedPaymentMethod,
    'roles': AppRole,
}


def _serialize_asset(kind, row):
    data = {'id': row.id, 'name': row.name, 'is_active': getattr(row, 'is_active', True)}
    if kind == 'categories':
        data['description'] = row.description or ''
        data['depreciation_rate'] = _money(row.depreciation_rate) if row.depreciation_rate is not None else None
    elif kind == 'types':
        data['description'] = row.description or ''
    elif kind == 'vendors':
        data.update({'phone': row.phone or '', 'email': row.email or '', 'address': row.address or ''})
    return data


def _apply_asset(kind, row, data):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    row.name = name
    if hasattr(row, 'is_active') and 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    if kind == 'categories':
        row.description = (data.get('description') or '').strip() or None
        row.depreciation_rate = _dec(data.get('depreciation_rate')) if data.get('depreciation_rate') not in (None, '') else None
    elif kind == 'types':
        row.description = (data.get('description') or '').strip() or None
    elif kind == 'vendors':
        row.phone = (data.get('phone') or '').strip()
        row.email = (data.get('email') or '').strip()
        row.address = (data.get('address') or '').strip()
    row.save()
    return row


def serialize_contract(row):
    return {
        'id': row.id,
        'vendor_id': row.vendor_id,
        'vendor_name': row.vendor.name if row.vendor_id else '',
        'title': row.title,
        'name': row.title,
        'start_date': row.start_date.isoformat() if row.start_date else '',
        'end_date': row.end_date.isoformat() if row.end_date else '',
        'amount': _money(row.amount),
        'notes': row.notes or '',
        'is_active': row.is_active,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def asset_config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if kind == 'vendor-contracts':
        if request.method == 'POST':
            data = request.data or {}
            vendor = _fk(AssetVendor, tenant, data.get('vendor_id'))
            title = (data.get('title') or data.get('name') or '').strip()
            if not vendor or not title:
                return Response({'detail': 'Vendor and title are required'}, status=400)
            row = AssetVendorContract.objects.create(
                tenant=tenant,
                vendor=vendor,
                title=title,
                start_date=_date(data.get('start_date')),
                end_date=_date(data.get('end_date')),
                amount=_dec(data.get('amount')),
                notes=(data.get('notes') or '').strip(),
                is_active=_bool(data.get('is_active'), True),
            )
            return Response(serialize_contract(row), status=201)
        qs = AssetVendorContract.objects.filter(tenant=tenant).select_related('vendor')
        return Response({
            'items': [serialize_contract(r) for r in qs],
            'options': {'vendors': _opt(AssetVendor.objects.filter(tenant=tenant, is_active=True).order_by('name'))},
        })
    model = ASSET_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    if request.method == 'POST':
        try:
            row = _apply_asset(kind, model(tenant=tenant), request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(_serialize_asset(kind, row), status=201)
    qs = model.objects.filter(tenant=tenant).order_by('name')
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(name__icontains=search)
    return Response({'items': [_serialize_asset(kind, r) for r in qs], 'options': {}})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def asset_config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if kind == 'vendor-contracts':
        try:
            row = AssetVendorContract.objects.select_related('vendor').get(id=pk, tenant=tenant)
        except AssetVendorContract.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        if request.method == 'DELETE':
            row.delete()
            return Response(status=204)
        if request.method in ('PATCH', 'PUT'):
            data = request.data or {}
            if data.get('vendor_id'):
                row.vendor = _fk(AssetVendor, tenant, data.get('vendor_id')) or row.vendor
            if data.get('title') or data.get('name'):
                row.title = (data.get('title') or data.get('name')).strip()
            if 'start_date' in data:
                row.start_date = _date(data.get('start_date'))
            if 'end_date' in data:
                row.end_date = _date(data.get('end_date'))
            if 'amount' in data:
                row.amount = _dec(data.get('amount'))
            if 'notes' in data:
                row.notes = (data.get('notes') or '').strip()
            if 'is_active' in data:
                row.is_active = _bool(data.get('is_active'))
            row.save()
        return Response(serialize_contract(row))
    model = ASSET_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    try:
        row = model.objects.get(id=pk, tenant=tenant)
    except model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        row.delete()
        return Response(status=204)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _apply_asset(kind, row, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
    return Response(_serialize_asset(kind, row))


# --- Broadcast ---
def serialize_message(row):
    cost = (row.unit_cost or Decimal('0')) * Decimal(row.recipient_count or 0)
    if row.channel != 'sms':
        cost = Decimal('0')
    count = row.recipient_count or 0
    return {
        'id': row.id,
        'title': row.title,
        'subject': row.title,
        'message': row.message,
        'content': row.message or '',
        'channel': row.channel,
        'recipient_type': row.channel or 'in_app',
        'priority': row.priority,
        'recipient_count': count,
        'recipients': [f'{count} recipient(s)'] if count else [],
        'message_number': f'BC-{row.id}',
        'unit_cost': _money(row.unit_cost),
        'cost': _money(cost),
        'sent_at': row.sent_at.isoformat() if row.sent_at else '',
        'created_at': row.created_at.isoformat() if row.created_at else '',
        'status': 'sent' if row.sent_at else 'draft',
        'created_by': _uname(row.created_by),
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def broadcast_messages(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    settings = _settings(tenant)
    if request.method == 'POST':
        data = request.data or {}
        title = (data.get('title') or data.get('subject') or '').strip()
        body = (data.get('message') or data.get('content') or '').strip()
        if not title or not body:
            return Response({'detail': 'Title and message are required'}, status=400)
        channel = (data.get('channel') or 'in_app').strip()
        count = max(1, int(data.get('recipient_count') or 1))
        unit = settings.sms_unit_cost if channel == 'sms' else Decimal('0')
        row = BroadcastMessage.objects.create(
            tenant=tenant,
            title=title,
            message=body,
            message_type=(data.get('message_type') or 'announcement'),
            priority=(data.get('priority') or 'medium'),
            channel=channel,
            recipient_count=count,
            unit_cost=unit,
            send_to_all=_bool(data.get('send_to_all'), True),
            sent_at=timezone.now(),
            created_by=request.user,
        )
        return Response(serialize_message(row), status=201)
    qs = BroadcastMessage.objects.filter(tenant=tenant).order_by('-id')
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(message__icontains=search))
    status_filter = (request.query_params.get('status') or '').strip()
    if status_filter == 'sent':
        qs = qs.exclude(sent_at=None)
    elif status_filter == 'draft':
        qs = qs.filter(sent_at=None)
    items = [serialize_message(r) for r in qs[:400]]
    return Response({
        'items': items,
        'messages': items,
        'options': {
            'channels': [{'id': 'in_app', 'name': 'In-app'}, {'id': 'sms', 'name': 'SMS'}],
            'priorities': [{'id': 'low', 'name': 'Low'}, {'id': 'medium', 'name': 'Medium'}, {'id': 'high', 'name': 'High'}, {'id': 'urgent', 'name': 'Urgent'}],
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sms_cost_report(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    qs = BroadcastMessage.objects.filter(
        tenant=tenant, channel='sms', sent_at__date__gte=start, sent_at__date__lte=end
    )
    grouped = defaultdict(lambda: {'messages': 0, 'recipients': 0, 'cost': 0.0})
    for row in qs:
        day = row.sent_at.date().isoformat() if row.sent_at else ''
        grouped[day]['messages'] += 1
        grouped[day]['recipients'] += row.recipient_count or 0
        grouped[day]['cost'] += float((row.unit_cost or 0) * (row.recipient_count or 0))
    rows = [{'date': k, **v, 'cost': round(v['cost'], 4)} for k, v in sorted(grouped.items())]
    return Response({
        'columns': ['Date', 'Messages', 'Recipients', 'Cost'],
        'rows': rows,
        'summary': {
            'messages': sum(r['messages'] for r in rows),
            'recipients': sum(r['recipients'] for r in rows),
            'cost': round(sum(r['cost'] for r in rows), 4),
        },
    })


# --- Utilities masters ---
def _serialize_util(kind, row):
    if kind == 'blog':
        return {
            'id': row.id,
            'title': row.title,
            'name': row.title,
            'body': row.body or '',
            'is_published': row.is_published,
            'published_at': row.published_at.isoformat() if row.published_at else '',
            'is_active': row.is_published,
        }
    if kind == 'images':
        return {
            'id': row.id,
            'caption': row.caption or '',
            'name': row.caption or row.image_url,
            'image_url': row.image_url,
            'sort_order': row.sort_order,
            'is_active': row.is_active,
        }
    if kind == 'terminals':
        return {
            'id': row.id,
            'name': row.name,
            'kind': row.kind,
            'distance_km': _money(row.distance_km),
            'notes': row.notes or '',
            'is_active': row.is_active,
        }
    if kind == 'payment-methods':
        return {
            'id': row.id,
            'name': row.name,
            'description': row.description or '',
            'is_active': row.is_active,
        }
    if kind == 'roles':
        return {
            'id': row.id,
            'name': row.name,
            'description': row.description or '',
            'modules': row.modules or '',
            'is_active': row.is_active,
        }
    return {'id': row.id}


def _apply_util(kind, row, data):
    if kind == 'blog':
        title = (data.get('title') or data.get('name') or '').strip()
        if not title:
            raise ValueError('Title is required')
        row.title = title
        row.body = (data.get('body') or data.get('description') or '').strip()
        row.is_published = _bool(data.get('is_published') or data.get('is_active'), False)
        row.published_at = _date(data.get('published_at')) or (date.today() if row.is_published else None)
    elif kind == 'images':
        url = (data.get('image_url') or '').strip()
        if not url:
            raise ValueError('Image URL is required')
        row.image_url = url
        row.caption = (data.get('caption') or data.get('name') or '').strip()
        row.sort_order = int(data.get('sort_order') or 0)
        if 'is_active' in data:
            row.is_active = _bool(data.get('is_active'))
    elif kind == 'terminals':
        name = (data.get('name') or '').strip()
        if not name:
            raise ValueError('Name is required')
        row.name = name
        row.kind = (data.get('kind') or 'airport').strip()
        row.distance_km = _dec(data.get('distance_km'))
        row.notes = (data.get('notes') or '').strip()
        if 'is_active' in data:
            row.is_active = _bool(data.get('is_active'))
    elif kind == 'payment-methods':
        name = (data.get('name') or '').strip()
        if not name:
            raise ValueError('Name is required')
        row.name = name
        row.description = (data.get('description') or '').strip()
        if 'is_active' in data:
            row.is_active = _bool(data.get('is_active'))
    elif kind == 'roles':
        name = (data.get('name') or '').strip()
        if not name:
            raise ValueError('Name is required')
        row.name = name
        row.description = (data.get('description') or '').strip()
        row.modules = (data.get('modules') or '').strip()
        if 'is_active' in data:
            row.is_active = _bool(data.get('is_active'))
    row.save()
    return row


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def util_config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    if kind == 'roles':
        from api.rbac import has_capability, CAP_MANAGE_USERS
        user = request.user
        if not user.is_superuser and (user.role or '') != 'admin' and not has_capability(user.role, CAP_MANAGE_USERS):
            return Response({'detail': 'Admin only'}, status=403)
    tenant = _tenant(request)
    model = UTIL_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    if request.method == 'POST':
        try:
            row = _apply_util(kind, model(tenant=tenant), request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(_serialize_util(kind, row), status=201)
    qs = model.objects.filter(tenant=tenant)
    search = (request.query_params.get('search') or '').strip()
    if search:
        if kind == 'blog':
            qs = qs.filter(Q(title__icontains=search) | Q(body__icontains=search))
        elif hasattr(model, 'name'):
            qs = qs.filter(name__icontains=search)
        elif kind == 'images':
            qs = qs.filter(Q(caption__icontains=search) | Q(image_url__icontains=search))
    return Response({
        'items': [_serialize_util(kind, r) for r in qs[:400]],
        'options': {
            'terminal_kinds': [
                {'id': 'airport', 'name': 'Airport'},
                {'id': 'bus', 'name': 'Bus'},
                {'id': 'train', 'name': 'Train'},
                {'id': 'ferry', 'name': 'Ferry'},
            ],
        },
    })


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def util_config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    if kind == 'roles':
        from api.rbac import has_capability, CAP_MANAGE_USERS
        user = request.user
        if not user.is_superuser and (user.role or '') != 'admin' and not has_capability(user.role, CAP_MANAGE_USERS):
            return Response({'detail': 'Admin only'}, status=403)
    tenant = _tenant(request)
    model = UTIL_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    try:
        row = model.objects.get(id=pk, tenant=tenant)
    except model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        row.delete()
        return Response(status=204)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _apply_util(kind, row, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
    return Response(_serialize_util(kind, row))


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def additional_configs(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    row = _settings(tenant)
    if request.method != 'GET':
        data = request.data or {}
        for key in ('check_in_time', 'check_out_time', 'night_audit_time'):
            if data.get(key):
                setattr(row, key, str(data.get(key)).strip())
        if 'tax_percent' in data:
            row.tax_percent = _dec(data.get('tax_percent'))
        if 'service_charge_percent' in data:
            row.service_charge_percent = _dec(data.get('service_charge_percent'))
        if 'sms_unit_cost' in data:
            row.sms_unit_cost = _dec(data.get('sms_unit_cost'))
        row.save()
    return Response({
        'check_in_time': row.check_in_time,
        'check_out_time': row.check_out_time,
        'tax_percent': _money(row.tax_percent),
        'service_charge_percent': _money(row.service_charge_percent),
        'sms_unit_cost': _money(row.sms_unit_cost),
        'night_audit_time': row.night_audit_time,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def account_permissions(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    from api.rbac import has_capability, CAP_MANAGE_USERS
    user = request.user
    if not user.is_superuser and (user.role or '') != 'admin' and not has_capability(user.role, CAP_MANAGE_USERS):
        return Response({'detail': 'Admin only'}, status=403)
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        try:
            user = User.objects.get(id=int(data.get('user_id')), tenant=tenant)
        except (User.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'User is required'}, status=400)
        row, _ = UserAccountPermission.objects.get_or_create(tenant=tenant, user=user)
        row.can_post_vouchers = _bool(data.get('can_post_vouchers'), False)
        row.can_view_reports = _bool(data.get('can_view_reports'), True)
        row.can_manage_coa = _bool(data.get('can_manage_coa'), False)
        row.save()
        return Response(_perm(row), status=201)
    users = User.objects.filter(tenant=tenant).order_by('username')
    perms = {p.user_id: p for p in UserAccountPermission.objects.filter(tenant=tenant)}
    items = []
    for user in users:
        row = perms.get(user.id)
        items.append({
            'id': row.id if row else user.id,
            'user_id': user.id,
            'name': _uname(user) or user.username,
            'username': user.username,
            'role': user.role,
            'can_post_vouchers': row.can_post_vouchers if row else False,
            'can_view_reports': row.can_view_reports if row else False,
            'can_manage_coa': row.can_manage_coa if row else False,
        })
    return Response({
        'items': items,
        'options': {'users': [{'id': u.id, 'name': _uname(u) or u.username} for u in users]},
    })


def _perm(row):
    return {
        'id': row.id,
        'user_id': row.user_id,
        'name': _uname(row.user),
        'can_post_vouchers': row.can_post_vouchers,
        'can_view_reports': row.can_view_reports,
        'can_manage_coa': row.can_manage_coa,
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_log(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    qs = AuditLog.objects.filter(tenant=tenant, created_at__date__gte=start, created_at__date__lte=end).select_related('user')
    rows = [
        {
            'when': r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
            'user': _uname(r.user),
            'action': r.action,
            'entity': r.entity,
            'reference': r.reference or '',
            'details': r.details or '',
        }
        for r in qs[:500]
    ]
    return Response({
        'columns': ['When', 'User', 'Action', 'Entity', 'Reference', 'Details'],
        'rows': rows,
        'summary': {'entries': len(rows)},
    })


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    if request.method == 'POST':
        cache.clear()
        return Response({'ok': True, 'cleared_at': timezone.now().isoformat(), 'detail': 'Application cache cleared.'})
    return Response({'ok': True, 'detail': 'POST to clear the application cache.'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def backup(request):
    from api.models import CatalogRecord, Reservation, Room, Guest, JournalEntry

    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        cache.clear()
        counts = {
            'reservations': Reservation.objects.filter(tenant=tenant).count(),
            'rooms': Room.objects.filter(tenant=tenant).count(),
            'guests': Guest.objects.filter(tenant=tenant).count(),
            'vouchers': JournalEntry.objects.filter(tenant=tenant).count(),
        }
        stamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        notes = (
            f'Reservations {counts["reservations"]}, rooms {counts["rooms"]}, '
            f'guests {counts["guests"]}, vouchers {counts["vouchers"]}'
        )
        row = CatalogRecord.objects.create(
            tenant=tenant,
            kind='utilities_backup',
            name=f'Snapshot {stamp}',
            code=timezone.now().strftime('%Y%m%d%H%M%S'),
            status='ok',
            notes=notes,
        )
        return Response({
            'id': row.id,
            'name': row.name,
            'notes': notes,
            'detail': 'Snapshot recorded and application cache flushed.',
            'counts': counts,
        }, status=201)
    items = [
        {
            'id': row.id,
            'name': row.name,
            'code': row.code,
            'status': row.status,
            'notes': row.notes,
            'created_at': row.created_at.isoformat() if row.created_at else '',
        }
        for row in CatalogRecord.objects.filter(tenant=tenant, kind='utilities_backup').order_by('-id')[:100]
    ]
    return Response({'items': items})
