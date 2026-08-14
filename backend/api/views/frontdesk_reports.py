"""Frontdesk operational reports from reservations, folios, and audit logs."""
from collections import defaultdict
from datetime import date, datetime, timedelta
import re

from django.db.models import Q, Sum
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    AccountTransaction,
    AccountType,
    AgentFundRequest,
    AuditLog,
    BillItem,
    BillPayment,
    BookingAgent,
    FnbExpense,
    Order,
    OrderStatus,
    Reservation,
    ReservationStatus,
    Room,
)
from api.views import deny_if_no_tenant

DEAD = {ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW}
STAYING = {
    ReservationStatus.PENDING,
    ReservationStatus.CONFIRMED,
    ReservationStatus.CHECKED_IN,
    ReservationStatus.CHECKED_OUT,
}


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _date(value):
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def _period(request):
    today = date.today()
    start = _date(request.query_params.get('from')) or today.replace(day=1)
    end = _date(request.query_params.get('to')) or today
    if end < start:
        start, end = end, start
    return start, end


def _days(start, end):
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _money(value):
    return float(value or 0)


def _uname(user):
    if not user:
        return 'Unknown'
    full = f'{user.first_name or ""} {user.last_name or ""}'.strip()
    return full or user.username or user.email or 'Unknown'


def _gname(res):
    if not res.guest_id:
        return ''
    return f'{res.guest.first_name} {res.guest.last_name}'.strip()


def _room(res):
    return res.room.room_number if res.room_id else ''


def _rtype(res):
    if res.room_id and res.room.room_type_id:
        return res.room.room_type.name
    return ''


def _nights(res):
    if not res.check_in_date or not res.check_out_date:
        return 1
    n = (res.check_out_date.date() - res.check_in_date.date()).days
    return n if n > 0 else 1


def _d(dt):
    if not dt:
        return ''
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    return dt.isoformat()


def _res(tenant):
    return Reservation.objects.select_related(
        'guest', 'room', 'room__room_type', 'created_by'
    ).filter(tenant=tenant)


def _occupying(tenant, day):
    return _res(tenant).filter(
        status__in=STAYING,
        check_in_date__date__lte=day,
        check_out_date__date__gt=day,
    )


def _board(res):
    if getattr(res, 'board_type', None):
        return res.board_type
    notes = f'{res.notes or ""}\n{res.special_requests or ""}'
    match = re.search(r'Board:\s*(.+)', notes)
    return match.group(1).strip() if match else ''


def _transport(res):
    notes = res.notes or ''
    if 'Transport:' not in notes:
        return None
    pickup = drop = vehicle = ''
    pm = re.search(r'pickup=([^;]*)', notes)
    dm = re.search(r'drop=([^;]*)', notes)
    vm = re.search(r'vehicle=([^\n]*)', notes)
    if pm:
        pickup = pm.group(1).strip()
    if dm:
        drop = dm.group(1).strip()
    if vm:
        vehicle = vm.group(1).strip()
    has_pick = pickup and pickup.lower() != 'no'
    has_drop = drop and drop.lower() != 'no'
    if not has_pick and not has_drop:
        return None
    return {'pickup': pickup if has_pick else '', 'drop': drop if has_drop else '', 'vehicle': vehicle}


def _ok(columns, rows, summary=None):
    return Response({'columns': columns, 'rows': rows, 'summary': summary or {}})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def frontdesk_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    start, end = _period(request)
    handler = REPORTS.get(kind)
    if not handler:
        return Response({'detail': f'Unknown report: {kind}'}, status=400)
    return handler(tenant, start, end, request)


def report_booking(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(created_at__date__gte=start, created_at__date__lte=end).order_by('created_at')
    for res in qs:
        rows.append({
            'date': _d(res.created_at),
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'room_type': _rtype(res),
            'check_in': _d(res.check_in_date),
            'check_out': _d(res.check_out_date),
            'nights': _nights(res),
            'status': res.status,
            'source': res.source or '',
            'agent': res.booking_agent or '',
            'total': _money(res.total_amount),
            'user': _uname(res.created_by),
        })
    return _ok(
        ['Booked', 'Number', 'Guest', 'Room', 'Type', 'Check-in', 'Check-out', 'Nights', 'Status', 'Source', 'Agent', 'Total', 'User'],
        rows,
        {'bookings': len(rows), 'amount': round(sum(r['total'] for r in rows), 2)},
    )


def report_cancel_no_show(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(
        status__in=[ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW],
        updated_at__date__gte=start,
        updated_at__date__lte=end,
    ).order_by('-updated_at')
    for res in qs:
        rows.append({
            'date': _d(res.updated_at or res.created_at),
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'check_in': _d(res.check_in_date),
            'check_out': _d(res.check_out_date),
            'status': res.status,
            'total': _money(res.total_amount),
            'notes': (res.notes or '')[:80],
        })
    return _ok(
        ['Date', 'Number', 'Guest', 'Room', 'Check-in', 'Check-out', 'Status', 'Total', 'Notes'],
        rows,
        {'count': len(rows), 'amount': round(sum(r['total'] for r in rows), 2)},
    )


def report_arr_dep_detail(tenant, start, end, request, expected=False):
    rows = []
    arr_qs = _res(tenant).filter(check_in_date__date__gte=start, check_in_date__date__lte=end)
    dep_qs = _res(tenant).filter(check_out_date__date__gte=start, check_out_date__date__lte=end)
    if expected:
        arr_qs = arr_qs.filter(status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
        dep_qs = dep_qs.filter(status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN])
    else:
        arr_qs = arr_qs.exclude(status__in=DEAD)
        dep_qs = dep_qs.exclude(status__in=DEAD)
    for res in arr_qs.order_by('check_in_date'):
        rows.append({
            'date': _d(res.check_in_date),
            'type': 'Arrival',
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'room_type': _rtype(res),
            'status': res.status,
            'pax': (res.adults or 0) + (res.children or 0),
            'phone': res.guest.phone if res.guest_id else '',
        })
    for res in dep_qs.order_by('check_out_date'):
        rows.append({
            'date': _d(res.check_out_date),
            'type': 'Departure',
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'room_type': _rtype(res),
            'status': res.status,
            'pax': (res.adults or 0) + (res.children or 0),
            'phone': res.guest.phone if res.guest_id else '',
        })
    rows.sort(key=lambda r: (r['date'], r['type'], r['room']))
    return _ok(
        ['Date', 'Type', 'Number', 'Guest', 'Room', 'Room type', 'Status', 'Pax', 'Phone'],
        rows,
        {
            'arrivals': sum(1 for r in rows if r['type'] == 'Arrival'),
            'departures': sum(1 for r in rows if r['type'] == 'Departure'),
        },
    )


def report_arr_dep_summary(tenant, start, end, request, expected=False):
    detail = report_arr_dep_detail(tenant, start, end, request, expected=expected)
    grouped = defaultdict(lambda: {'arrivals': 0, 'departures': 0, 'arr_pax': 0, 'dep_pax': 0})
    for row in detail.data['rows']:
        key = row['date']
        if row['type'] == 'Arrival':
            grouped[key]['arrivals'] += 1
            grouped[key]['arr_pax'] += row['pax']
        else:
            grouped[key]['departures'] += 1
            grouped[key]['dep_pax'] += row['pax']
    rows = [{'date': day, **grouped[day.isoformat()]} for day in _days(start, end)]
    return _ok(
        ['Date', 'Arrivals', 'Arr. pax', 'Departures', 'Dep. pax'],
        rows,
        {
            'arrivals': sum(r['arrivals'] for r in rows),
            'departures': sum(r['departures'] for r in rows),
        },
    )


def report_inhouse(tenant, start, end, request):
    qs = _res(tenant).filter(status=ReservationStatus.CHECKED_IN).order_by('room__room_number')
    grouped = defaultdict(lambda: {'rooms': 0, 'pax': 0, 'rate': 0.0, 'due': 0.0})
    detail = []
    for res in qs:
        rt = _rtype(res) or 'Unassigned'
        grouped[rt]['rooms'] += 1
        grouped[rt]['pax'] += (res.adults or 0) + (res.children or 0)
        grouped[rt]['rate'] += _money(res.room_rate)
        grouped[rt]['due'] += _money(res.balance)
        detail.append({
            'room': _room(res),
            'room_type': rt,
            'guest': _gname(res),
            'check_in': _d(res.check_in_date),
            'check_out': _d(res.check_out_date),
            'pax': (res.adults or 0) + (res.children or 0),
            'rate': _money(res.room_rate),
            'due': _money(res.balance),
        })
    rows = [{'room_type': k, **v} for k, v in sorted(grouped.items())]
    return _ok(
        ['Room type', 'Rooms', 'Pax', 'Rate total', 'Due'],
        rows,
        {
            'in_house': len(detail),
            'pax': sum(r['pax'] for r in rows),
            'due': round(sum(r['due'] for r in rows), 2),
        },
    )


def report_daily_sales(tenant, start, end, request):
    rows = []
    total_rooms = Room.objects.filter(tenant=tenant, is_active=True).count()
    for day in _days(start, end):
        occ = list(_occupying(tenant, day))
        revenue = sum(_money(r.room_rate) for r in occ)
        extra = 0.0
        for item in BillItem.objects.filter(
            bill__tenant=tenant,
            charge_date__date=day,
        ).exclude(item_type='room_charge'):
            extra += _money(item.line_total)
        fnb = Order.objects.filter(
            tenant=tenant, created_at__date=day
        ).exclude(status=OrderStatus.CANCELLED).aggregate(s=Sum('total_amount'))['s']
        fnb_amt = _money(fnb)
        occ_n = len(occ)
        rows.append({
            'date': day.isoformat(),
            'occupied': occ_n,
            'occupancy_pct': round((occ_n / total_rooms * 100) if total_rooms else 0, 1),
            'room_revenue': round(revenue, 2),
            'extras': round(extra, 2),
            'fnb': round(fnb_amt, 2),
            'total': round(revenue + extra + fnb_amt, 2),
            'adr': round(revenue / occ_n, 2) if occ_n else 0,
        })
    return _ok(
        ['Date', 'Occupied', 'Occ. %', 'Room revenue', 'Extras', 'F&B', 'Total', 'ADR'],
        rows,
        {'total': round(sum(r['total'] for r in rows), 2)},
    )


def report_checklist(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(
        check_in_date__date__gte=start,
        check_in_date__date__lte=end,
        status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED],
    ).order_by('check_in_date')
    for res in qs:
        guest = res.guest
        missing = []
        if not res.room_id:
            missing.append('room')
        if guest and not (guest.phone or guest.mobile):
            missing.append('phone')
        if guest and not guest.id_number:
            missing.append('ID')
        if not res.paid_amount:
            missing.append('advance')
        rows.append({
            'check_in': _d(res.check_in_date),
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res) or '—',
            'phone': (guest.phone or guest.mobile or '') if guest else '',
            'id_number': (guest.id_number or '') if guest else '',
            'advance': _money(res.paid_amount),
            'missing': ', '.join(missing) or 'OK',
        })
    return _ok(
        ['Check-in', 'Number', 'Guest', 'Room', 'Phone', 'ID', 'Advance', 'Missing'],
        rows,
        {'arrivals': len(rows), 'incomplete': sum(1 for r in rows if r['missing'] != 'OK')},
    )


def report_pickup(tenant, start, end, request):
    rows = []
    qs = _res(tenant).exclude(status__in=DEAD).filter(
        Q(check_in_date__date__gte=start, check_in_date__date__lte=end)
        | Q(check_out_date__date__gte=start, check_out_date__date__lte=end)
    )
    for res in qs.order_by('check_in_date'):
        tr = _transport(res)
        if not tr:
            continue
        rows.append({
            'check_in': _d(res.check_in_date),
            'check_out': _d(res.check_out_date),
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'pickup': tr['pickup'],
            'drop': tr['drop'],
            'vehicle': tr['vehicle'],
            'phone': res.guest.phone if res.guest_id else '',
        })
    return _ok(
        ['Check-in', 'Check-out', 'Number', 'Guest', 'Room', 'Pickup', 'Drop', 'Vehicle', 'Phone'],
        rows,
        {'trips': len(rows)},
    )


def report_board(tenant, start, end, request):
    grouped = defaultdict(lambda: {'guests': 0, 'pax': 0, 'nights': 0})
    qs = _occupying(tenant, end) if start == end else _res(tenant).filter(
        status__in=STAYING,
        check_in_date__date__lte=end,
        check_out_date__date__gt=start,
    )
    for res in qs:
        board = _board(res) or 'Room Only'
        grouped[board]['guests'] += 1
        grouped[board]['pax'] += (res.adults or 0) + (res.children or 0)
        grouped[board]['nights'] += _nights(res)
    rows = [{'board': k, **v} for k, v in sorted(grouped.items())]
    return _ok(
        ['Board', 'Reservations', 'Pax', 'Nights'],
        rows,
        {'reservations': sum(r['guests'] for r in rows)},
    )


def report_addons(tenant, start, end, request):
    rows = []
    items = BillItem.objects.select_related('bill', 'bill__reservation', 'bill__guest').filter(
        bill__tenant=tenant,
        charge_date__date__gte=start,
        charge_date__date__lte=end,
    ).exclude(item_type='room_charge').order_by('charge_date')
    for item in items:
        res = item.bill.reservation
        rows.append({
            'date': _d(item.charge_date),
            'reservation': res.reservation_number if res else '',
            'guest': _gname(res) if res else (item.bill.guest.full_name if item.bill.guest_id else ''),
            'description': item.description,
            'type': item.item_type or 'extra',
            'qty': _money(item.quantity),
            'amount': _money(item.line_total),
        })
    return _ok(
        ['Date', 'Reservation', 'Guest', 'Description', 'Type', 'Qty', 'Amount'],
        rows,
        {'amount': round(sum(r['amount'] for r in rows), 2)},
    )


def report_payout(tenant, start, end, request):
    rows = []
    for row in AgentFundRequest.objects.select_related('agent', 'requested_by').filter(
        tenant=tenant, request_date__gte=start, request_date__lte=end
    ).order_by('request_date'):
        rows.append({
            'date': row.request_date.isoformat(),
            'number': row.request_number,
            'agent': row.agent.name if row.agent_id else '',
            'amount': _money(row.amount),
            'status': row.status,
            'user': _uname(row.requested_by),
            'notes': row.notes or '',
        })
    return _ok(
        ['Date', 'Number', 'Agent', 'Amount', 'Status', 'User', 'Notes'],
        rows,
        {'amount': round(sum(r['amount'] for r in rows), 2)},
    )


def report_guest(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(
        check_in_date__date__lte=end,
        check_out_date__date__gte=start,
    ).exclude(status=ReservationStatus.CANCELLED).order_by('check_in_date')
    for res in qs:
        g = res.guest
        rows.append({
            'guest': _gname(res),
            'phone': (g.phone or g.mobile or '') if g else '',
            'email': (g.email or '') if g else '',
            'nationality': (g.nationality or '') if g else '',
            'room': _room(res),
            'check_in': _d(res.check_in_date),
            'check_out': _d(res.check_out_date),
            'status': res.status,
            'source': res.source or '',
            'vip': 'Yes' if g and g.is_vip else 'No',
        })
    return _ok(
        ['Guest', 'Phone', 'Email', 'Nationality', 'Room', 'Check-in', 'Check-out', 'Status', 'Source', 'VIP'],
        rows,
        {'guests': len(rows)},
    )


def report_police(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(
        Q(status=ReservationStatus.CHECKED_IN)
        | Q(check_in_date__date__gte=start, check_in_date__date__lte=end, status__in=STAYING)
    ).order_by('room__room_number', 'check_in_date')
    seen = set()
    for res in qs:
        if res.id in seen:
            continue
        seen.add(res.id)
        g = res.guest
        rows.append({
            'room': _room(res),
            'guest': _gname(res),
            'gender': (g.gender or '') if g else '',
            'nationality': (g.nationality or '') if g else '',
            'id_type': (g.id_type or '') if g else '',
            'id_number': (g.id_number or '') if g else '',
            'address': ((g.address_line1 or '') + ' ' + (g.city or '')).strip() if g else '',
            'check_in': _d(res.actual_check_in or res.check_in_date),
            'check_out': _d(res.check_out_date),
            'status': res.status,
        })
    return _ok(
        ['Room', 'Guest', 'Gender', 'Nationality', 'ID type', 'ID number', 'Address', 'Check-in', 'Check-out', 'Status'],
        rows,
        {'guests': len(rows)},
    )


def report_guest_due(tenant, start, end, request):
    rows = []
    qs = _res(tenant).filter(
        status__in=[ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT, ReservationStatus.CONFIRMED],
        balance__gt=0,
    ).order_by('-balance')
    for res in qs:
        rows.append({
            'number': res.reservation_number,
            'guest': _gname(res),
            'room': _room(res),
            'status': res.status,
            'check_out': _d(res.check_out_date),
            'total': _money(res.total_amount),
            'paid': _money(res.paid_amount),
            'due': _money(res.balance),
            'phone': res.guest.phone if res.guest_id else '',
        })
    return _ok(
        ['Number', 'Guest', 'Room', 'Status', 'Check-out', 'Total', 'Paid', 'Due', 'Phone'],
        rows,
        {'due': round(sum(r['due'] for r in rows), 2), 'folios': len(rows)},
    )


def report_occupied(tenant, start, end, request):
    rows = []
    for day in _days(start, end):
        for res in _occupying(tenant, day).order_by('room__room_number'):
            rows.append({
                'date': day.isoformat(),
                'room': _room(res),
                'room_type': _rtype(res),
                'guest': _gname(res),
                'status': res.status,
                'rate': _money(res.room_rate),
                'pax': (res.adults or 0) + (res.children or 0),
            })
    return _ok(
        ['Date', 'Room', 'Type', 'Guest', 'Status', 'Rate', 'Pax'],
        rows,
        {'nights': len(rows)},
    )


def report_revenue(tenant, start, end, request):
    room = 0.0
    for day in _days(start, end):
        room += sum(_money(r.room_rate) for r in _occupying(tenant, day))
    extras = BillItem.objects.filter(
        bill__tenant=tenant, charge_date__date__gte=start, charge_date__date__lte=end
    ).exclude(item_type='room_charge').aggregate(s=Sum('line_total'))['s']
    fnb = Order.objects.filter(
        tenant=tenant, created_at__date__gte=start, created_at__date__lte=end
    ).exclude(status=OrderStatus.CANCELLED).aggregate(s=Sum('total_amount'))['s']
    extra_amt = _money(extras)
    fnb_amt = _money(fnb)
    rows = [
        {'source': 'Room', 'amount': round(room, 2)},
        {'source': 'Add-ons / extras', 'amount': round(extra_amt, 2)},
        {'source': 'F&B', 'amount': round(fnb_amt, 2)},
    ]
    return _ok(
        ['Source', 'Amount'],
        rows,
        {'total': round(room + extra_amt + fnb_amt, 2)},
    )


def report_manager(tenant, start, end, request):
    total_rooms = Room.objects.filter(tenant=tenant, is_active=True).count()
    days = _days(start, end)
    occ_nights = 0
    room_rev = 0.0
    for day in days:
        occ = list(_occupying(tenant, day))
        occ_nights += len(occ)
        room_rev += sum(_money(r.room_rate) for r in occ)
    avail = total_rooms * len(days)
    arr = _res(tenant).filter(check_in_date__date__gte=start, check_in_date__date__lte=end).exclude(status__in=DEAD).count()
    dep = _res(tenant).filter(check_out_date__date__gte=start, check_out_date__date__lte=end).exclude(status__in=DEAD).count()
    inhouse = _res(tenant).filter(status=ReservationStatus.CHECKED_IN).count()
    due = _res(tenant).filter(balance__gt=0).aggregate(s=Sum('balance'))['s']
    collected = BillPayment.objects.filter(
        bill__tenant=tenant, payment_date__date__gte=start, payment_date__date__lte=end
    ).aggregate(s=Sum('amount'))['s']
    rows = [
        {'metric': 'Available room nights', 'value': avail},
        {'metric': 'Occupied room nights', 'value': occ_nights},
        {'metric': 'Occupancy %', 'value': round(occ_nights / avail * 100, 1) if avail else 0},
        {'metric': 'Room revenue', 'value': round(room_rev, 2)},
        {'metric': 'ADR', 'value': round(room_rev / occ_nights, 2) if occ_nights else 0},
        {'metric': 'RevPAR', 'value': round(room_rev / avail, 2) if avail else 0},
        {'metric': 'Arrivals', 'value': arr},
        {'metric': 'Departures', 'value': dep},
        {'metric': 'In-house now', 'value': inhouse},
        {'metric': 'Collections', 'value': _money(collected)},
        {'metric': 'Guest due', 'value': _money(due)},
    ]
    return _ok(['Metric', 'Value'], rows, {'occupancy_nights': occ_nights, 'room_revenue': round(room_rev, 2)})


def report_night_audit(tenant, start, end, request):
    day = end
    total_rooms = Room.objects.filter(tenant=tenant, is_active=True).count()
    occ = list(_occupying(tenant, day))
    arr = _res(tenant).filter(check_in_date__date=day).exclude(status__in=DEAD).count()
    dep = _res(tenant).filter(check_out_date__date=day).exclude(status__in=DEAD).count()
    room_rev = sum(_money(r.room_rate) for r in occ)
    collected = BillPayment.objects.filter(bill__tenant=tenant, payment_date__date=day).aggregate(s=Sum('amount'))['s']
    extras = BillItem.objects.filter(bill__tenant=tenant, charge_date__date=day).exclude(item_type='room_charge').aggregate(s=Sum('line_total'))['s']
    fnb = Order.objects.filter(tenant=tenant, created_at__date=day).exclude(status=OrderStatus.CANCELLED).aggregate(s=Sum('total_amount'))['s']
    due = sum(_money(r.balance) for r in _res(tenant).filter(status=ReservationStatus.CHECKED_IN))
    rows = [
        {'metric': 'Audit date', 'value': day.isoformat()},
        {'metric': 'Rooms in hotel', 'value': total_rooms},
        {'metric': 'Occupied tonight', 'value': len(occ)},
        {'metric': 'Occupancy %', 'value': round(len(occ) / total_rooms * 100, 1) if total_rooms else 0},
        {'metric': 'Arrivals today', 'value': arr},
        {'metric': 'Departures today', 'value': dep},
        {'metric': 'Room revenue', 'value': round(room_rev, 2)},
        {'metric': 'Extras posted', 'value': _money(extras)},
        {'metric': 'F&B sales', 'value': _money(fnb)},
        {'metric': 'Collections', 'value': _money(collected)},
        {'metric': 'In-house due', 'value': round(due, 2)},
    ]
    return _ok(['Metric', 'Value'], rows, {'occupied': len(occ), 'room_revenue': round(room_rev, 2)})


def report_income_expense(tenant, start, end, request):
    room = 0.0
    for day in _days(start, end):
        room += sum(_money(r.room_rate) for r in _occupying(tenant, day))
    extras = _money(BillItem.objects.filter(
        bill__tenant=tenant, charge_date__date__gte=start, charge_date__date__lte=end
    ).exclude(item_type='room_charge').aggregate(s=Sum('line_total'))['s'])
    fnb = _money(Order.objects.filter(
        tenant=tenant, created_at__date__gte=start, created_at__date__lte=end
    ).exclude(status=OrderStatus.CANCELLED).aggregate(s=Sum('total_amount'))['s'])
    acct_exp = 0.0
    txs = AccountTransaction.objects.select_related('account', 'journal_entry').filter(
        tenant=tenant,
        transaction_date__gte=start,
        transaction_date__lte=end,
        journal_entry__is_posted=True,
        account__account_type=AccountType.EXPENSE,
    )
    for tx in txs:
        if tx.transaction_type == 'debit':
            acct_exp += _money(tx.amount)
        else:
            acct_exp -= _money(tx.amount)
    fnb_exp = _money(FnbExpense.objects.filter(
        tenant=tenant, expense_date__gte=start, expense_date__lte=end
    ).aggregate(s=Sum('amount'))['s'])
    income = room + extras + fnb
    expense = acct_exp + fnb_exp
    rows = [
        {'side': 'Income', 'head': 'Room', 'amount': round(room, 2)},
        {'side': 'Income', 'head': 'Add-ons', 'amount': round(extras, 2)},
        {'side': 'Income', 'head': 'F&B', 'amount': round(fnb, 2)},
        {'side': 'Expense', 'head': 'Accounts expenses', 'amount': round(acct_exp, 2)},
        {'side': 'Expense', 'head': 'F&B expenses', 'amount': round(fnb_exp, 2)},
    ]
    return _ok(
        ['Side', 'Head', 'Amount'],
        rows,
        {'income': round(income, 2), 'expense': round(expense, 2), 'net': round(income - expense, 2)},
    )


def report_monthly_sales(tenant, start, end, request):
    grouped = defaultdict(lambda: {'room': 0.0, 'extras': 0.0, 'fnb': 0.0})
    for day in _days(start, end):
        key = day.strftime('%Y-%m')
        grouped[key]['room'] += sum(_money(r.room_rate) for r in _occupying(tenant, day))
    extras = BillItem.objects.filter(
        bill__tenant=tenant, charge_date__date__gte=start, charge_date__date__lte=end
    ).exclude(item_type='room_charge')
    for item in extras:
        day = item.charge_date.date() if item.charge_date else start
        grouped[day.strftime('%Y-%m')]['extras'] += _money(item.line_total)
    orders = Order.objects.filter(
        tenant=tenant, created_at__date__gte=start, created_at__date__lte=end
    ).exclude(status=OrderStatus.CANCELLED)
    for order in orders:
        grouped[order.created_at.date().strftime('%Y-%m')]['fnb'] += _money(order.total_amount)
    rows = [
        {
            'month': k,
            'room': round(v['room'], 2),
            'extras': round(v['extras'], 2),
            'fnb': round(v['fnb'], 2),
            'total': round(v['room'] + v['extras'] + v['fnb'], 2),
        }
        for k, v in sorted(grouped.items())
    ]
    return _ok(
        ['Month', 'Room', 'Extras', 'F&B', 'Total'],
        rows,
        {'total': round(sum(r['total'] for r in rows), 2)},
    )


def report_agent_commission(tenant, start, end, request):
    agents = {a.name.lower(): a for a in BookingAgent.objects.filter(tenant=tenant)}
    grouped = defaultdict(lambda: {'bookings': 0, 'room_nights': 0, 'revenue': 0.0, 'rate': 0.0})
    qs = _res(tenant).exclude(status__in=DEAD).filter(
        created_at__date__gte=start, created_at__date__lte=end
    ).exclude(booking_agent='')
    for res in qs:
        name = (res.booking_agent or '').strip()
        if not name:
            continue
        agent = agents.get(name.lower())
        rate = float(agent.commission_rate or 0) if agent else 0
        grouped[name]['bookings'] += 1
        grouped[name]['room_nights'] += _nights(res)
        grouped[name]['revenue'] += _money(res.total_amount)
        grouped[name]['rate'] = rate
    rows = [
        {
            'agent': k,
            'bookings': v['bookings'],
            'nights': v['room_nights'],
            'revenue': round(v['revenue'], 2),
            'rate_pct': v['rate'],
            'commission': round(v['revenue'] * v['rate'] / 100, 2),
        }
        for k, v in sorted(grouped.items())
    ]
    return _ok(
        ['Agent', 'Bookings', 'Nights', 'Revenue', 'Rate %', 'Commission'],
        rows,
        {'commission': round(sum(r['commission'] for r in rows), 2)},
    )


def report_daily_collection(tenant, start, end, request):
    grouped = defaultdict(lambda: {'cash': 0.0, 'card': 0.0, 'other': 0.0, 'count': 0})
    pays = BillPayment.objects.select_related('bill').filter(
        bill__tenant=tenant, payment_date__date__gte=start, payment_date__date__lte=end
    )
    for pay in pays:
        day = pay.payment_date.date().isoformat()
        amt = _money(pay.amount)
        grouped[day]['count'] += 1
        method = (pay.payment_method or 'other').lower()
        if method == 'cash':
            grouped[day]['cash'] += amt
        elif method == 'card':
            grouped[day]['card'] += amt
        else:
            grouped[day]['other'] += amt
    rows = []
    for day in _days(start, end):
        vals = grouped[day.isoformat()]
        rows.append({
            'date': day.isoformat(),
            'receipts': vals['count'],
            'cash': round(vals['cash'], 2),
            'card': round(vals['card'], 2),
            'other': round(vals['other'], 2),
            'total': round(vals['cash'] + vals['card'] + vals['other'], 2),
        })
    return _ok(
        ['Date', 'Receipts', 'Cash', 'Card', 'Other', 'Total'],
        rows,
        {'total': round(sum(r['total'] for r in rows), 2)},
    )


def report_monthly_collection(tenant, start, end, request):
    grouped = defaultdict(float)
    pays = BillPayment.objects.filter(
        bill__tenant=tenant, payment_date__date__gte=start, payment_date__date__lte=end
    )
    for pay in pays:
        grouped[pay.payment_date.date().strftime('%Y-%m')] += _money(pay.amount)
    rows = [{'month': k, 'amount': round(v, 2)} for k, v in sorted(grouped.items())]
    return _ok(['Month', 'Amount'], rows, {'total': round(sum(r['amount'] for r in rows), 2)})


def report_userwise_collection(tenant, start, end, request):
    grouped = defaultdict(lambda: {'receipts': 0, 'amount': 0.0})
    pays = BillPayment.objects.select_related('created_by').filter(
        bill__tenant=tenant, payment_date__date__gte=start, payment_date__date__lte=end
    )
    for pay in pays:
        name = _uname(pay.created_by)
        grouped[name]['receipts'] += 1
        grouped[name]['amount'] += _money(pay.amount)
    rows = [
        {'user': k, 'receipts': v['receipts'], 'amount': round(v['amount'], 2)}
        for k, v in sorted(grouped.items())
    ]
    return _ok(
        ['User', 'Receipts', 'Amount'],
        rows,
        {'total': round(sum(r['amount'] for r in rows), 2)},
    )


def report_audit(tenant, start, end, request):
    qs = AuditLog.objects.select_related('user').filter(
        tenant=tenant, created_at__date__gte=start, created_at__date__lte=end
    ).order_by('-created_at')[:1000]
    rows = []
    for row in qs:
        rows.append({
            'when': row.created_at.strftime('%Y-%m-%d %H:%M') if row.created_at else '',
            'user': _uname(row.user),
            'action': row.action,
            'entity': row.entity,
            'reference': row.reference or '',
            'details': row.details or '',
        })
    return _ok(
        ['When', 'User', 'Action', 'Entity', 'Reference', 'Details'],
        rows,
        {'events': len(rows)},
    )


REPORTS = {
    'booking': report_booking,
    'cancel-no-show': report_cancel_no_show,
    'arrival-departure-summary': lambda t, s, e, r: report_arr_dep_summary(t, s, e, r, False),
    'arrival-departure-detail': lambda t, s, e, r: report_arr_dep_detail(t, s, e, r, False),
    'inhouse-summary': report_inhouse,
    'expected-arrival-departure-summary': lambda t, s, e, r: report_arr_dep_summary(t, s, e, r, True),
    'expected-arrival-departure-detail': lambda t, s, e, r: report_arr_dep_detail(t, s, e, r, True),
    'daily-sales': report_daily_sales,
    'booking-checklist': report_checklist,
    'pickup-drop': report_pickup,
    'board': report_board,
    'add-ons': report_addons,
    'payout': report_payout,
    'guest': report_guest,
    'police': report_police,
    'guest-due': report_guest_due,
    'daily-occupied-rooms': report_occupied,
    'revenue': report_revenue,
    'manager': report_manager,
    'night-audit': report_night_audit,
    'income-expense': report_income_expense,
    'monthly-sales': report_monthly_sales,
    'agent-commission': report_agent_commission,
    'daily-collection': report_daily_collection,
    'monthly-collection': report_monthly_collection,
    'userwise-daily-collection': report_userwise_collection,
    'audit-trail': report_audit,
}
