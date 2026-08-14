"""Banquet masters, events, folios, venue forecast, and reports."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models.banquet import (
    BanquetEvent,
    BanquetEventLine,
    BanquetEventPayment,
    BanquetItem,
    BanquetPackage,
    BanquetService,
    BanquetSession,
    BanquetVendor,
    BanquetVenue,
)
from api.views import deny_if_no_tenant

SIMPLE_KINDS = {
    'venues': BanquetVenue,
    'vendors': BanquetVendor,
    'services': BanquetService,
    'items': BanquetItem,
    'packages': BanquetPackage,
    'sessions': BanquetSession,
}

LIVE = ('enquiry', 'confirmed', 'in_progress')
OPEN_FOLIO = ('enquiry', 'confirmed', 'in_progress', 'completed')


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


def _money(value):
    return float(value or 0)


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs, extra=None):
    rows = []
    for row in qs:
        item = {'id': row.id, 'name': row.name}
        if extra:
            item.update(extra(row))
        rows.append(item)
    return rows


def _due(event):
    due = (event.total_amount or Decimal('0')) - (event.paid_amount or Decimal('0'))
    return due if due > 0 else Decimal('0')


def _seed(tenant):
    if not BanquetVenue.objects.filter(tenant=tenant).exists():
        BanquetVenue.objects.create(tenant=tenant, name='Grand Ballroom', code='BALL', capacity=300, hourly_rate=15000)
        BanquetVenue.objects.create(tenant=tenant, name='Garden Lawn', code='LAWN', capacity=200, hourly_rate=8000)
        BanquetVenue.objects.create(tenant=tenant, name='Conference Hall', code='CONF', capacity=80, hourly_rate=5000)
    if not BanquetSession.objects.filter(tenant=tenant).exists():
        BanquetSession.objects.create(tenant=tenant, name='Morning', start_time='09:00', end_time='12:00')
        BanquetSession.objects.create(tenant=tenant, name='Lunch', start_time='12:00', end_time='16:00')
        BanquetSession.objects.create(tenant=tenant, name='Evening', start_time='16:00', end_time='20:00')
        BanquetSession.objects.create(tenant=tenant, name='Dinner', start_time='19:00', end_time='23:00')
    if not BanquetService.objects.filter(tenant=tenant).exists():
        for name, price in (
            ('Decoration', 25000),
            ('Sound System', 12000),
            ('Stage & Lighting', 18000),
            ('Photography', 15000),
        ):
            BanquetService.objects.create(tenant=tenant, name=name, unit_price=price)
    if not BanquetItem.objects.filter(tenant=tenant).exists():
        for name, unit, price in (
            ('Extra Chair', 'Pcs', 80),
            ('Round Table', 'Pcs', 400),
            ('Projector', 'Pcs', 2500),
            ('Floral Centerpiece', 'Pcs', 600),
        ):
            BanquetItem.objects.create(tenant=tenant, name=name, unit=unit, unit_price=price)
    if not BanquetPackage.objects.filter(tenant=tenant).exists():
        BanquetPackage.objects.create(tenant=tenant, name='Standard Buffet', price_per_pax=1200)
        BanquetPackage.objects.create(tenant=tenant, name='Premium Buffet', price_per_pax=1800)
        BanquetPackage.objects.create(tenant=tenant, name='Cocktail Package', price_per_pax=900)
    if not BanquetVendor.objects.filter(tenant=tenant).exists():
        BanquetVendor.objects.create(
            tenant=tenant, name='Floral Decor Co.', service_type='Decoration', phone='01700000001', rate=20000
        )
        BanquetVendor.objects.create(
            tenant=tenant, name='City DJ', service_type='Entertainment', phone='01700000002', rate=15000
        )


def _options(tenant):
    return {
        'venues': _opt(
            BanquetVenue.objects.filter(tenant=tenant, is_active=True).order_by('name'),
            lambda r: {'capacity': r.capacity, 'hourly_rate': _money(r.hourly_rate)},
        ),
        'vendors': _opt(
            BanquetVendor.objects.filter(tenant=tenant, is_active=True).order_by('name'),
            lambda r: {'rate': _money(r.rate), 'service_type': r.service_type or ''},
        ),
        'services': _opt(
            BanquetService.objects.filter(tenant=tenant, is_active=True).order_by('name'),
            lambda r: {'unit_price': _money(r.unit_price)},
        ),
        'items': _opt(
            BanquetItem.objects.filter(tenant=tenant, is_active=True).order_by('name'),
            lambda r: {'unit_price': _money(r.unit_price), 'unit': r.unit or ''},
        ),
        'packages': _opt(
            BanquetPackage.objects.filter(tenant=tenant, is_active=True).order_by('name'),
            lambda r: {'price_per_pax': _money(r.price_per_pax)},
        ),
        'sessions': _opt(
            BanquetSession.objects.filter(tenant=tenant, is_active=True).order_by('start_time', 'name'),
            lambda r: {'start_time': r.start_time or '', 'end_time': r.end_time or ''},
        ),
        'event_types': [
            {'id': 'wedding', 'name': 'Wedding'},
            {'id': 'conference', 'name': 'Conference'},
            {'id': 'birthday', 'name': 'Birthday'},
            {'id': 'corporate', 'name': 'Corporate'},
            {'id': 'reception', 'name': 'Reception'},
            {'id': 'other', 'name': 'Other'},
        ],
        'payment_methods': [
            {'id': 'cash', 'name': 'Cash'},
            {'id': 'card', 'name': 'Card'},
            {'id': 'bank', 'name': 'Bank'},
            {'id': 'mobile', 'name': 'Mobile'},
        ],
    }


def serialize_named(kind, row):
    data = {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'is_active': row.is_active,
    }
    if kind == 'venues':
        data.update({
            'code': row.code or '',
            'capacity': row.capacity,
            'hourly_rate': _money(row.hourly_rate),
        })
    elif kind == 'vendors':
        data.update({
            'phone': row.phone or '',
            'email': row.email or '',
            'service_type': row.service_type or '',
            'rate': _money(row.rate),
        })
    elif kind == 'services':
        data['unit_price'] = _money(row.unit_price)
    elif kind == 'items':
        data.update({'unit': row.unit or '', 'unit_price': _money(row.unit_price)})
    elif kind == 'packages':
        data['price_per_pax'] = _money(row.price_per_pax)
    elif kind == 'sessions':
        data.update({'start_time': row.start_time or '', 'end_time': row.end_time or ''})
    return data


def serialize_line(line):
    return {
        'id': line.id,
        'line_type': line.line_type,
        'ref_id': line.service_id or line.item_id or line.vendor_id,
        'name': line.name,
        'quantity': _money(line.quantity),
        'unit_price': _money(line.unit_price),
        'amount': _money(line.amount),
        'notes': line.notes or '',
    }


def serialize_event(event, include_lines=False):
    due = _due(event)
    data = {
        'id': event.id,
        'number': event.number,
        'name': event.name,
        'event_type': event.event_type,
        'contact_name': event.contact_name or '',
        'phone': event.phone or '',
        'email': event.email or '',
        'company': event.company or '',
        'venue_id': event.venue_id,
        'venue_name': event.venue.name if event.venue_id else '',
        'session_id': event.session_id,
        'session_name': event.session.name if event.session_id else '',
        'event_date': event.event_date.isoformat() if event.event_date else '',
        'start_time': event.start_time or (event.session.start_time if event.session_id else ''),
        'end_time': event.end_time or (event.session.end_time if event.session_id else ''),
        'pax': event.pax,
        'package_id': event.package_id,
        'package_name': event.package.name if event.package_id else '',
        'package_amount': _money(event.package_amount),
        'lines_amount': _money(event.lines_amount),
        'total_amount': _money(event.total_amount),
        'paid_amount': _money(event.paid_amount),
        'due': _money(due),
        'status': event.status,
        'notes': event.notes or '',
        'can_confirm': event.status == 'enquiry',
        'can_start': event.status == 'confirmed',
        'can_complete': event.status in ('confirmed', 'in_progress'),
        'can_cancel': event.status in LIVE,
        'can_pay': event.status in OPEN_FOLIO and due > 0,
    }
    if include_lines:
        data['lines'] = [serialize_line(line) for line in event.lines.all()]
        data['payments'] = [
            {
                'id': pay.id,
                'pay_date': pay.pay_date.isoformat(),
                'amount': _money(pay.amount),
                'method': pay.method,
                'notes': pay.notes or '',
            }
            for pay in event.payments.all()
        ]
    return data


def _next_number(tenant):
    last = BanquetEvent.objects.filter(tenant=tenant).order_by('-id').first()
    seq = (last.id if last else 0) + 1
    return f'EVT-{seq:05d}'


def _apply_named(kind, row, data):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    row.name = name
    row.description = (data.get('description') or '').strip() or None
    if 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    if kind == 'venues':
        row.code = (data.get('code') or '').strip()
        row.capacity = _int(data.get('capacity'), 0)
        row.hourly_rate = _dec(data.get('hourly_rate'))
    elif kind == 'vendors':
        row.phone = (data.get('phone') or '').strip()
        row.email = (data.get('email') or '').strip()
        row.service_type = (data.get('service_type') or '').strip()
        row.rate = _dec(data.get('rate'))
    elif kind == 'services':
        row.unit_price = _dec(data.get('unit_price'))
    elif kind == 'items':
        row.unit = (data.get('unit') or 'Pcs').strip() or 'Pcs'
        row.unit_price = _dec(data.get('unit_price'))
    elif kind == 'packages':
        row.price_per_pax = _dec(data.get('price_per_pax'))
    elif kind == 'sessions':
        row.start_time = (data.get('start_time') or '').strip()
        row.end_time = (data.get('end_time') or '').strip()
    row.save()
    return row


def _search_named(qs, kind, search):
    if not search:
        return qs
    q = Q(name__icontains=search)
    if kind == 'venues':
        q |= Q(code__icontains=search)
    elif kind == 'vendors':
        q |= Q(phone__icontains=search) | Q(service_type__icontains=search)
    return qs.filter(q)


def _replace_lines(event, tenant, lines):
    event.lines.all().delete()
    total = Decimal('0')
    for raw in lines or []:
        line_type = (raw.get('line_type') or '').strip()
        if line_type not in ('service', 'item', 'vendor'):
            continue
        qty = _dec(raw.get('quantity'), '1')
        if qty <= 0:
            continue
        service = item = vendor = None
        name = (raw.get('name') or '').strip()
        unit_price = _dec(raw.get('unit_price'))
        if line_type == 'service':
            service = _fk(BanquetService, tenant, raw.get('ref_id') or raw.get('service_id'))
            if service:
                name = name or service.name
                if raw.get('unit_price') in (None, ''):
                    unit_price = service.unit_price
        elif line_type == 'item':
            item = _fk(BanquetItem, tenant, raw.get('ref_id') or raw.get('item_id'))
            if item:
                name = name or item.name
                if raw.get('unit_price') in (None, ''):
                    unit_price = item.unit_price
        else:
            vendor = _fk(BanquetVendor, tenant, raw.get('ref_id') or raw.get('vendor_id'))
            if vendor:
                name = name or vendor.name
                if raw.get('unit_price') in (None, ''):
                    unit_price = vendor.rate
        if not name:
            continue
        amount = qty * unit_price
        BanquetEventLine.objects.create(
            event=event,
            line_type=line_type,
            service=service,
            item=item,
            vendor=vendor,
            name=name,
            quantity=qty,
            unit_price=unit_price,
            amount=amount,
            notes=(raw.get('notes') or '').strip(),
        )
        total += amount
    return total


def _recalc(event):
    pkg = Decimal('0')
    if event.package_id:
        pkg = (event.package.price_per_pax or Decimal('0')) * Decimal(event.pax or 0)
    lines = event.lines.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    event.package_amount = pkg
    event.lines_amount = lines
    event.total_amount = pkg + lines
    paid = event.payments.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    event.paid_amount = paid
    event.save()
    return event


def _overlap_conflict(tenant, venue, event_date, session, exclude_id=None):
    if not venue or not event_date:
        return None
    qs = BanquetEvent.objects.filter(
        tenant=tenant,
        venue=venue,
        event_date=event_date,
        status__in=LIVE,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if session:
        qs = qs.filter(Q(session=session) | Q(session__isnull=True, start_time=session.start_time))
    return qs.first()


def _save_event(tenant, data, user=None, instance=None):
    name = (data.get('name') or '').strip()
    event_date = _date(data.get('event_date'))
    if not name:
        raise ValueError('Event name is required')
    if not event_date:
        raise ValueError('Event date is required')
    venue = _fk(BanquetVenue, tenant, data.get('venue_id'))
    session = _fk(BanquetSession, tenant, data.get('session_id'))
    package = _fk(BanquetPackage, tenant, data.get('package_id'))
    event = instance or BanquetEvent(tenant=tenant, number=_next_number(tenant), created_by=user)
    if instance and instance.status not in LIVE:
        raise ValueError('Only enquiry / confirmed / in-progress events can be edited')
    conflict = _overlap_conflict(tenant, venue, event_date, session, exclude_id=event.id if event.id else None)
    if conflict:
        raise ValueError(f'Venue already booked for that session ({conflict.number} {conflict.name})')
    event.name = name
    event.event_type = (data.get('event_type') or 'other').strip() or 'other'
    event.contact_name = (data.get('contact_name') or '').strip()
    event.phone = (data.get('phone') or '').strip()
    event.email = (data.get('email') or '').strip()
    event.company = (data.get('company') or '').strip()
    event.venue = venue
    event.session = session
    event.event_date = event_date
    event.start_time = (data.get('start_time') or (session.start_time if session else '') or '').strip()
    event.end_time = (data.get('end_time') or (session.end_time if session else '') or '').strip()
    event.pax = max(0, _int(data.get('pax'), 0))
    event.package = package
    event.notes = (data.get('notes') or '').strip()
    if not instance:
        event.status = 'enquiry'
    event.save()
    if 'lines' in data:
        _replace_lines(event, tenant, data.get('lines'))
    return _recalc(event)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    model = SIMPLE_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    _seed(tenant)
    if request.method == 'POST':
        try:
            row = _apply_named(kind, model(tenant=tenant), request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_named(kind, row), status=status.HTTP_201_CREATED)
    qs = model.objects.filter(tenant=tenant).order_by('name')
    qs = _search_named(qs, kind, (request.query_params.get('search') or '').strip())
    items = [serialize_named(kind, row) for row in qs[:500]]
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
    model = SIMPLE_KINDS.get(kind)
    if not model:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        row = model.objects.get(id=pk, tenant=tenant)
    except model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        if kind == 'venues' and row.events.exists():
            return Response({'detail': 'Venue has events. Deactivate it instead of deleting.'}, status=400)
        if kind == 'packages' and row.events.exists():
            return Response({'detail': 'Set menu is used on events. Deactivate instead of deleting.'}, status=400)
        if kind == 'sessions' and row.events.exists():
            return Response({'detail': 'Session is used on events. Deactivate instead of deleting.'}, status=400)
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _apply_named(kind, row, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_named(kind, row))
    return Response(serialize_named(kind, row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def events(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    _seed(tenant)
    if request.method == 'POST':
        try:
            event = _save_event(tenant, request.data or {}, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_event(event, include_lines=True), status=status.HTTP_201_CREATED)
    qs = BanquetEvent.objects.filter(tenant=tenant).select_related('venue', 'session', 'package')
    pending = str(request.query_params.get('pending') or '').lower() in ('1', 'true', 'yes')
    if pending:
        qs = qs.filter(status__in=OPEN_FOLIO)
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(
            Q(number__icontains=search)
            | Q(name__icontains=search)
            | Q(contact_name__icontains=search)
            | Q(phone__icontains=search)
        )
    start = _date(request.query_params.get('from'))
    end = _date(request.query_params.get('to'))
    if start:
        qs = qs.filter(event_date__gte=start)
    if end:
        qs = qs.filter(event_date__lte=end)
    items = [serialize_event(row) for row in qs[:500]]
    if pending:
        items = [row for row in items if row['due'] > 0]
    return Response({
        'items': items,
        'options': _options(tenant),
        'summary': {
            'events': len(items),
            'total': round(sum(row['total_amount'] for row in items), 2),
            'due': round(sum(row['due'] for row in items), 2),
        },
    })


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def event_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        event = BanquetEvent.objects.select_related('venue', 'session', 'package').get(id=pk, tenant=tenant)
    except BanquetEvent.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method in ('PATCH', 'PUT'):
        try:
            event = _save_event(tenant, request.data or {}, user=request.user, instance=event)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_event(event, include_lines=True))
    return Response(serialize_event(event, include_lines=True))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def event_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        event = BanquetEvent.objects.select_related('venue', 'session', 'package').get(id=pk, tenant=tenant)
    except BanquetEvent.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    action = (request.data or {}).get('action')
    data = request.data or {}
    if action == 'confirm':
        if event.status != 'enquiry':
            return Response({'detail': 'Only enquiry events can be confirmed'}, status=400)
        event.status = 'confirmed'
        event.save(update_fields=['status', 'updated_at'])
    elif action == 'start':
        if event.status != 'confirmed':
            return Response({'detail': 'Confirm the event before starting'}, status=400)
        event.status = 'in_progress'
        event.save(update_fields=['status', 'updated_at'])
    elif action == 'complete':
        if event.status not in ('confirmed', 'in_progress'):
            return Response({'detail': 'Only confirmed or in-progress events can be completed'}, status=400)
        event.status = 'completed'
        event.save(update_fields=['status', 'updated_at'])
    elif action == 'cancel':
        if event.status not in LIVE:
            return Response({'detail': 'This event cannot be cancelled'}, status=400)
        event.status = 'cancelled'
        event.save(update_fields=['status', 'updated_at'])
    elif action == 'pay':
        amount = _dec(data.get('amount'))
        if amount <= 0:
            return Response({'detail': 'Payment amount is required'}, status=400)
        due = _due(event)
        if amount > due:
            return Response({'detail': 'Amount exceeds folio due'}, status=400)
        BanquetEventPayment.objects.create(
            event=event,
            pay_date=_date(data.get('pay_date')) or date.today(),
            amount=amount,
            method=(data.get('method') or 'cash').strip() or 'cash',
            notes=(data.get('notes') or '').strip(),
            created_by=request.user,
        )
        _recalc(event)
    else:
        return Response({'detail': f'Unknown action: {action}'}, status=400)
    event.refresh_from_db()
    return Response(serialize_event(event, include_lines=True))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def venue_forecast(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    _seed(tenant)
    start = _date(request.query_params.get('from')) or date.today()
    end = _date(request.query_params.get('to')) or (start + timedelta(days=13))
    if end < start:
        start, end = end, start
    if (end - start).days > 31:
        end = start + timedelta(days=31)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    venues = list(BanquetVenue.objects.filter(tenant=tenant, is_active=True).order_by('name'))
    sessions = list(BanquetSession.objects.filter(tenant=tenant, is_active=True).order_by('start_time', 'name'))
    booked = BanquetEvent.objects.filter(
        tenant=tenant,
        event_date__gte=start,
        event_date__lte=end,
        status__in=LIVE,
        venue__isnull=False,
    ).select_related('venue', 'session')
    by_key = defaultdict(list)
    for event in booked:
        by_key[(event.venue_id, event.event_date)].append(event)
    rows = []
    for venue in venues:
        cells = []
        for day in days:
            events = by_key.get((venue.id, day), [])
            labels = []
            for event in events:
                sess = event.session.name if event.session_id else (event.start_time or 'Booked')
                labels.append(f'{sess}: {event.name}')
            cells.append({
                'date': day.isoformat(),
                'state': 'occupied' if events else 'available',
                'label': '; '.join(labels) if labels else 'Free',
                'count': len(events),
            })
        rows.append({
            'venue_id': venue.id,
            'venue': venue.name,
            'capacity': venue.capacity,
            'cells': cells,
        })
    return Response({
        'from': start.isoformat(),
        'to': end.isoformat(),
        'dates': [d.isoformat() for d in days],
        'sessions': [{'id': s.id, 'name': s.name, 'start_time': s.start_time, 'end_time': s.end_time} for s in sessions],
        'rows': rows,
    })


def _period(request):
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    if end < start:
        start, end = end, start
    return start, end


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def banquet_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    start, end = _period(request)
    events_qs = BanquetEvent.objects.filter(
        tenant=tenant, event_date__gte=start, event_date__lte=end
    ).exclude(status='cancelled').select_related('venue', 'session', 'package')

    if kind == 'events':
        rows = []
        for event in events_qs.order_by('event_date', 'number'):
            rows.append({
                'number': event.number,
                'date': event.event_date.isoformat(),
                'event': event.name,
                'type': event.event_type,
                'venue': event.venue.name if event.venue_id else '',
                'session': event.session.name if event.session_id else '',
                'pax': event.pax,
                'total': _money(event.total_amount),
                'paid': _money(event.paid_amount),
                'due': _money(_due(event)),
                'status': event.status,
            })
        return Response({
            'columns': ['No.', 'Date', 'Event', 'Type', 'Venue', 'Session', 'Pax', 'Total', 'Paid', 'Due', 'Status'],
            'rows': rows,
            'summary': {
                'events': len(rows),
                'pax': sum(r['pax'] for r in rows),
                'total': round(sum(r['total'] for r in rows), 2),
                'due': round(sum(r['due'] for r in rows), 2),
            },
        })

    if kind in ('services', 'items', 'set-menu'):
        line_type = {'services': 'service', 'items': 'item'}.get(kind)
        if kind == 'set-menu':
            grouped = defaultdict(lambda: {'events': 0, 'pax': 0, 'amount': 0.0})
            for event in events_qs:
                if not event.package_id:
                    continue
                key = event.package.name
                grouped[key]['events'] += 1
                grouped[key]['pax'] += event.pax
                grouped[key]['amount'] += _money(event.package_amount)
            rows = [
                {'set_menu': name, 'events': val['events'], 'pax': val['pax'], 'amount': round(val['amount'], 2)}
                for name, val in sorted(grouped.items())
            ]
            return Response({
                'columns': ['Set menu', 'Events', 'Pax', 'Amount'],
                'rows': rows,
                'summary': {
                    'menus': len(rows),
                    'amount': round(sum(r['amount'] for r in rows), 2),
                },
            })
        grouped = defaultdict(lambda: {'qty': 0.0, 'amount': 0.0})
        lines = BanquetEventLine.objects.filter(event__in=events_qs, line_type=line_type)
        for line in lines:
            grouped[line.name]['qty'] += float(line.quantity or 0)
            grouped[line.name]['amount'] += _money(line.amount)
        label = 'Service' if kind == 'services' else 'Item'
        rows = [
            {'name': name, 'quantity': round(val['qty'], 2), 'amount': round(val['amount'], 2)}
            for name, val in sorted(grouped.items())
        ]
        return Response({
            'columns': [label, 'Quantity', 'Amount'],
            'rows': rows,
            'summary': {
                'lines': len(rows),
                'amount': round(sum(r['amount'] for r in rows), 2),
            },
        })

    return Response({'detail': f'Unknown report: {kind}'}, status=400)
