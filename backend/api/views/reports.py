"""Live operational reports from reservations, F&B, accounts, and inventory."""
from datetime import date

from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import JournalEntry, Order, Purchase, Reservation, Room, RoomType
from api.views import deny_if_no_tenant


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _from_reservations(tenant, kind='', limit=300):
    qs = Reservation.objects.select_related('guest', 'room', 'room__room_type').filter(tenant=tenant)
    today = date.today()
    if 'cancel' in kind or 'no-show' in kind or 'noshow' in kind:
        qs = qs.filter(status__in=['cancelled', 'no_show'])
    elif 'inhouse' in kind:
        qs = qs.filter(status='checked_in')
    elif 'arrival' in kind:
        qs = qs.exclude(status__in=['cancelled', 'no_show'])
        if 'expected' in kind:
            qs = qs.filter(check_in_date__date__gte=today, status__in=['confirmed', 'pending'])
        else:
            qs = qs.filter(check_in_date__date=today)
    elif 'departure' in kind:
        qs = qs.exclude(status__in=['cancelled', 'no_show'])
        if 'expected' in kind:
            qs = qs.filter(check_out_date__date__gte=today, status__in=['confirmed', 'checked_in'])
        else:
            qs = qs.filter(check_out_date__date=today)
    elif 'occupied' in kind:
        qs = qs.filter(status='checked_in')
    elif 'guest-due' in kind or 'guest_due' in kind:
        qs = qs.filter(status__in=['checked_in', 'checked_out']).exclude(balance=0)
    elif 'police' in kind:
        qs = qs.filter(status__in=['checked_in', 'checked_out'])
    qs = qs.order_by('-check_in_date')[:limit]
    items = []
    for row in qs:
        guest = f'{row.guest.first_name} {row.guest.last_name}' if row.guest_id else ''
        room = row.room.room_number if row.room_id else ''
        dates = ''
        if row.check_in_date and row.check_out_date:
            dates = f'{row.check_in_date.date()} → {row.check_out_date.date()}'
        items.append({
            'id': row.id,
            'name': row.reservation_number,
            'code': guest or room,
            'amount': float(row.total_amount or 0),
            'status': row.status,
            'notes': dates,
        })
    return items


def _from_orders(tenant, limit=300):
    qs = Order.objects.filter(tenant=tenant).order_by('-id')[:limit]
    items = []
    for row in qs:
        items.append({
            'id': row.id,
            'name': getattr(row, 'order_number', None) or f'ORD-{row.id}',
            'code': row.guest_name or '',
            'amount': float(row.total_amount or 0),
            'status': row.status,
            'notes': row.notes or row.special_instructions or '',
        })
    return items


def _from_purchases(tenant, limit=300):
    qs = Purchase.objects.filter(tenant=tenant).order_by('-id')[:limit]
    items = []
    for row in qs:
        items.append({
            'id': row.id,
            'name': getattr(row, 'purchase_number', None) or f'PUR-{row.id}',
            'code': getattr(row, 'supplier_id', None) and str(row.supplier_id) or '',
            'amount': float(getattr(row, 'total_amount', None) or 0),
            'status': getattr(row, 'status', '') or '',
            'notes': '',
        })
    return items


def _from_journals(tenant, limit=300):
    qs = JournalEntry.objects.filter(tenant=tenant).order_by('-id')[:limit]
    items = []
    for row in qs:
        items.append({
            'id': row.id,
            'name': getattr(row, 'entry_number', None) or f'JV-{row.id}',
            'code': getattr(row, 'entry_type', None) or '',
            'amount': float(getattr(row, 'total_debit', None) or getattr(row, 'amount', None) or 0),
            'status': 'posted' if row.is_posted else 'draft',
            'notes': getattr(row, 'narration', None) or getattr(row, 'description', None) or '',
        })
    return items


def _availability(tenant, by_room=False):
    today = date.today()
    occupied_ids = set(
        Reservation.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'checked_in'],
            check_in_date__date__lte=today,
            check_out_date__date__gt=today,
            room_id__isnull=False,
        ).values_list('room_id', flat=True)
    )
    if by_room:
        items = []
        for room in Room.objects.select_related('room_type').filter(tenant=tenant, is_active=True).order_by('room_number')[:300]:
            busy = room.id in occupied_ids
            items.append({
                'id': room.id,
                'name': room.room_number,
                'code': room.room_type.name if room.room_type_id else '',
                'amount': float(room.rack_rate or room.room_type.base_rate or 0) if room.room_type_id else 0,
                'status': 'occupied' if busy else room.status,
                'notes': f'Floor {room.floor}' if room.floor is not None else '',
            })
        return items
    items = []
    for rt in RoomType.objects.filter(tenant=tenant, is_active=True):
        rooms = list(Room.objects.filter(tenant=tenant, room_type=rt, is_active=True))
        total = len(rooms)
        occupied = sum(1 for r in rooms if r.id in occupied_ids)
        free = max(0, total - occupied)
        items.append({
            'id': rt.id,
            'name': rt.name,
            'code': f'{total} rooms',
            'amount': free,
            'status': 'available' if free else 'full',
            'notes': f'{occupied} occupied today · {free} free',
        })
    return items


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_catalog(request):
    """Subscription-gated industry report catalog (hotel / resort / restaurant)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'reports': [], 'categories': [], 'total': 0})
    if not tenant.has_module('reports'):
        return Response(
            {'detail': 'Report Center is not enabled for this subscription.'},
            status=403,
        )
    from api.services.reports_catalog import catalog_payload

    return Response(
        catalog_payload(
            tenant,
            module=request.query_params.get('module'),
            category=request.query_params.get('category'),
            status=request.query_params.get('status'),
            search=request.query_params.get('q') or request.query_params.get('search'),
        )
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_report(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'items': []})
    kind = (request.query_params.get('kind') or '').lower()
    if 'forecast' in kind or 'availability' in kind or 'room-rate-schedule' in kind:
        items = _availability(tenant, by_room='availability' in kind or 'schedule' in kind)
    elif 'fnb' in kind:
        items = _from_orders(tenant)
    elif 'inventory' in kind or 'stock' in kind or 'consumption' in kind:
        items = _from_purchases(tenant)
    elif 'accounts' in kind or 'ledger' in kind or 'trial' in kind or 'cash-book' in kind or 'bank-book' in kind or 'profit' in kind or 'opening-balance' in kind or 'balance-sheet' in kind:
        items = _from_journals(tenant)
    else:
        items = _from_reservations(tenant, kind)
    return Response({'items': items, 'kind': kind})
