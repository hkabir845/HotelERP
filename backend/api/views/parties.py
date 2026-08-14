"""Party subsidiary ledger APIs — list, statement, aging, reconcile."""
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import ChartOfAccount, PartyAccount, PartyLedgerEntry, PartyType
from api.services.hotel_coa import ensure_hotel_coa
from api.services.hotel_gl import check_account_permission
from api.services.party_ledger import (
    get_or_create_party,
    party_aging,
    reconcile_control,
    sync_party_opening,
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


def _date(value):
    if not value:
        return None
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def serialize_party(row):
    return {
        'id': row.id,
        'code': row.code,
        'name': row.name,
        'party_type': row.party_type,
        'party_id': row.party_id,
        'control_account_id': row.control_account_id,
        'control_code': row.control_account.account_code,
        'control_name': row.control_account.account_name,
        'opening_balance': float(row.opening_balance or 0),
        'opening_balance_as_of': row.opening_balance_as_of.isoformat() if row.opening_balance_as_of else None,
        'balance': float(row.current_balance or 0),
        'is_active': row.is_active,
        'notes': row.notes or '',
    }


def serialize_entry(row):
    return {
        'id': row.id,
        'date': row.entry_date.isoformat(),
        'debit': float(row.debit or 0),
        'credit': float(row.credit or 0),
        'balance': float(row.balance_after or 0),
        'narration': row.narration or '',
        'journal_entry_id': row.journal_entry_id,
        'voucher': row.journal_entry.entry_number if row.journal_entry_id else None,
        'related_type': row.related_type,
        'related_id': row.related_id,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def party_accounts(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    ensure_hotel_coa(tenant)

    if request.method == 'POST':
        denied_perm = check_account_permission(request.user, 'can_manage_coa')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        data = request.data or {}
        name = (data.get('name') or '').strip()
        party_type = (data.get('party_type') or PartyType.OTHER).strip().lower()
        if not name:
            return Response({'detail': 'Name is required'}, status=400)
        if party_type not in PartyType.values:
            return Response({'detail': 'Invalid party type'}, status=400)
        try:
            party = get_or_create_party(
                tenant,
                party_type,
                name,
                party_id=data.get('party_id') or None,
                control_code=data.get('control_code') or None,
                loan_payable=bool(data.get('loan_payable')),
            )
            if 'opening_balance' in data or 'opening_balance_as_of' in data:
                party.opening_balance = _dec(data.get('opening_balance'))
                party.opening_balance_as_of = _date(data.get('opening_balance_as_of'))
                party.notes = data.get('notes') or party.notes
                party.save()
                sync_party_opening(party)
                party.refresh_from_db()
            elif data.get('notes') is not None:
                party.notes = data.get('notes') or ''
                party.save(update_fields=['notes', 'updated_at'])
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_party(party), status=201)

    qs = PartyAccount.objects.filter(tenant=tenant).select_related('control_account')
    ptype = (request.query_params.get('party_type') or '').strip()
    if ptype:
        qs = qs.filter(party_type=ptype)
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
    if request.query_params.get('active', '1') == '1':
        qs = qs.filter(is_active=True)
    control_id = request.query_params.get('control_account_id')
    if control_id:
        qs = qs.filter(control_account_id=control_id)

    items = [serialize_party(row) for row in qs.order_by('party_type', 'name')[:500]]
    return Response({
        'parties': items,
        'items': items,
        'party_types': [{'value': c.value, 'label': c.label} for c in PartyType],
        'total': len(items),
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def party_account_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = PartyAccount.objects.select_related('control_account').get(id=pk, tenant=tenant)
    except PartyAccount.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)

    if request.method == 'PATCH':
        denied_perm = check_account_permission(request.user, 'can_manage_coa')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        data = request.data or {}
        opening_changed = False
        if data.get('name'):
            row.name = data['name'].strip()
        if 'notes' in data:
            row.notes = data.get('notes') or ''
        if 'is_active' in data:
            row.is_active = data.get('is_active') in (True, 'true', '1', 1, 'on')
        if 'opening_balance' in data:
            row.opening_balance = _dec(data.get('opening_balance'))
            opening_changed = True
        if 'opening_balance_as_of' in data:
            row.opening_balance_as_of = _date(data.get('opening_balance_as_of'))
            opening_changed = True
        row.save()
        if opening_changed:
            sync_party_opening(row)
            row.refresh_from_db()
        return Response(serialize_party(row))

    start = _date(request.query_params.get('from'))
    end = _date(request.query_params.get('to'))
    entries = PartyLedgerEntry.objects.filter(party_account=row).select_related('journal_entry').order_by(
        'entry_date', 'id',
    )
    if start:
        entries = entries.filter(entry_date__gte=start)
    if end:
        entries = entries.filter(entry_date__lte=end)

    return Response({
        'party': serialize_party(row),
        'entries': [serialize_entry(e) for e in entries],
        'from': start.isoformat() if start else None,
        'to': end.isoformat() if end else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def party_aging_report(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    denied_perm = check_account_permission(request.user, 'can_view_reports')
    if denied_perm:
        return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
    as_of = _date(request.query_params.get('as_of'))
    ptype = (request.query_params.get('party_type') or '').strip() or None
    rows, totals = party_aging(tenant, party_type=ptype, as_of=as_of)
    return Response({
        'as_of': (as_of or datetime.now().date()).isoformat(),
        'party_type': ptype,
        'rows': rows,
        'totals': totals,
        'columns': ['Code', 'Name', 'Type', 'Current', '1-30', '31-60', '61-90', '90+', 'Total', 'Ledger bal'],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def party_reconcile(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    denied_perm = check_account_permission(request.user, 'can_view_reports')
    if denied_perm:
        return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
    ensure_hotel_coa(tenant)
    as_of = _date(request.query_params.get('as_of'))
    control_id = request.query_params.get('control_account_id')
    qs = ChartOfAccount.objects.filter(tenant=tenant, is_group=False, party_accounts__isnull=False).distinct()
    if control_id:
        qs = ChartOfAccount.objects.filter(tenant=tenant, id=control_id)
    results = [reconcile_control(tenant, acc, as_of=as_of) for acc in qs.order_by('account_code')]
    return Response({'results': results, 'as_of': (as_of or datetime.now().date()).isoformat()})
