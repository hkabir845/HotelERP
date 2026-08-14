"""Live chart of accounts, voucher posting, and accounting reports."""
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    AccountTransaction,
    AccountsPayable,
    AccountsReceivable,
    APPayment,
    ARPayment,
    Budget,
    ChartOfAccount,
    JournalEntry,
    PaymentStatus,
)
from api.services.hotel_coa import erp_defaults_payload
from api.services.coa_opening import sync_account_opening
from api.services.source_drill import build_voucher_drill_chain, resolve_source
from api.services.hotel_gl import (
    check_account_permission,
    ensure_hotel_accounts,
    post_ap_bill,
    post_ap_payment,
    post_ar_invoice,
    post_ar_payment,
    refresh_budget_actual,
    refresh_tenant_budgets,
)
from api.views import deny_if_no_tenant

VOUCHER_PREFIX = {
    'cash_payment': 'CPV',
    'bank_payment': 'BPV',
    'cash_receipt': 'CRV',
    'bank_receipt': 'BRV',
    'contra': 'CNV',
    'journal': 'JV',
}

NORMAL_DEBIT = {'asset', 'expense'}


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
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def _signed(account, txn_type, amount):
    amount = _dec(amount)
    if account.account_type in NORMAL_DEBIT:
        return amount if txn_type == 'debit' else -amount
    return amount if txn_type == 'credit' else -amount


def _next_number(tenant, voucher_type):
    prefix = VOUCHER_PREFIX.get(voucher_type, 'JV')
    count = JournalEntry.objects.filter(tenant=tenant, voucher_type=voucher_type).count() + 1
    return f'{prefix}-{tenant.id}-{count:05d}'


def ensure_default_accounts(tenant):
    """Seed the full built-in hotel chart (FSERP-style template)."""
    from api.services.hotel_coa import ensure_hotel_coa

    ensure_hotel_coa(tenant)


def serialize_account(row, include_children=False, children_map=None, balances=None):
    bal = (balances or {}).get(row.id)
    if bal is None:
        bal = row.current_balance
    data = {
        'id': row.id,
        'code': row.account_code,
        'name': row.account_name,
        'account_type': row.account_type,
        'parent_id': row.parent_account_id,
        'description': row.description or '',
        'opening_balance': float(row.opening_balance or 0),
        'opening_balance_as_of': row.opening_balance_as_of.isoformat() if getattr(row, 'opening_balance_as_of', None) else None,
        'opening_balance_journal_id': getattr(row, 'opening_balance_journal_id', None),
        'balance': float(bal or 0),
        'is_group': row.is_group,
        'is_active': row.is_active,
        'book': row.book or '',
    }
    if include_children:
        kids = (children_map or {}).get(row.id, [])
        data['children'] = [
            serialize_account(child, True, children_map, balances) for child in kids
        ]
    return data


def serialize_voucher(row, include_lines=False):
    created = ''
    if row.created_by_id:
        created = f'{row.created_by.first_name} {row.created_by.last_name}'.strip() or row.created_by.email
    lines = []
    if include_lines:
        lines = list(row.transactions.select_related('account').all())
    source = build_voucher_drill_chain(row, lines if include_lines else None)
    if not include_lines:
        source = resolve_source(
            row.tenant,
            entry_number=row.entry_number,
            journal_description=row.description,
        )
    payload = {
        'id': row.id,
        'voucher_number': row.entry_number,
        'voucher_type': row.voucher_type,
        'date': row.entry_date.isoformat() if row.entry_date else None,
        'amount': float(row.total_debit or 0),
        'description': row.description or '',
        'reference': row.reference or '',
        'status': 'posted' if row.is_posted else 'draft',
        'created_by': created,
        'total_debit': float(row.total_debit or 0),
        'total_credit': float(row.total_credit or 0),
        'related_type': source.get('related_type'),
        'related_id': source.get('related_id'),
        'source_label': source.get('source_label'),
        'source_path': source.get('source_path'),
        'source_description': source.get('source_description'),
        'drill_chain': source.get('drill_chain') or [],
    }
    if include_lines:
        payload['lines'] = [
            {
                'id': line.id,
                'account_id': line.account_id,
                'account_code': line.account.account_code,
                'account_name': line.account.account_name,
                'debit': float(line.amount if line.transaction_type == 'debit' else 0),
                'credit': float(line.amount if line.transaction_type == 'credit' else 0),
                'description': line.description or '',
                'related_type': line.related_type,
                'related_id': line.related_id,
                **{
                    k: v
                    for k, v in resolve_source(
                        row.tenant,
                        line.related_type,
                        line.related_id,
                        row.entry_number,
                        journal_description=line.description or row.description,
                    ).items()
                    if k in ('source_label', 'source_path', 'source_description')
                },
            }
            for line in lines
        ]
    return payload


def _book_account(tenant, book):
    return (
        ChartOfAccount.objects.filter(tenant=tenant, book=book, is_group=False, is_active=True)
        .order_by('id')
        .first()
    )


def _apply_lines(tenant, entry, lines, posted):
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    for raw in lines:
        account = ChartOfAccount.objects.filter(
            id=raw.get('account_id'), tenant=tenant, is_group=False
        ).first()
        if not account:
            raise ValueError('Each line needs a posting account (not a group)')
        debit = _dec(raw.get('debit'))
        credit = _dec(raw.get('credit'))
        if debit and credit:
            raise ValueError('A line cannot have both debit and credit')
        if not debit and not credit:
            continue
        txn_type = 'debit' if debit else 'credit'
        amount = debit or credit
        AccountTransaction.objects.create(
            tenant=tenant,
            journal_entry=entry,
            account=account,
            transaction_type=txn_type,
            amount=amount,
            description=raw.get('description') or entry.description,
            reference=entry.entry_number,
            transaction_date=entry.entry_date,
        )
        total_debit += debit
        total_credit += credit
        if posted:
            account.current_balance = (account.current_balance or 0) + _signed(account, txn_type, amount)
            account.save(update_fields=['current_balance', 'updated_at'])
    if total_debit != total_credit:
        raise ValueError(f'Debit {total_debit} must equal credit {total_credit}')
    if total_debit == 0:
        raise ValueError('Enter at least one amount')
    entry.total_debit = total_debit
    entry.total_credit = total_credit
    entry.save(update_fields=['total_debit', 'total_credit', 'updated_at'])


def _balance_as_of(account, as_of):
    qs = AccountTransaction.objects.filter(
        account=account,
        journal_entry__is_posted=True,
    )
    if as_of:
        qs = qs.filter(transaction_date__lte=as_of)
    debit = qs.filter(transaction_type='debit').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    credit = qs.filter(transaction_type='credit').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    # Journalized openings are already in transactions — do not double-count the field.
    if getattr(account, 'opening_balance_journal_id', None):
        opening = Decimal('0')
    else:
        opening = account.opening_balance or Decimal('0')
    if account.account_type in NORMAL_DEBIT:
        return opening + debit - credit, debit, credit
    return opening + credit - debit, debit, credit


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chart_of_accounts(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    ensure_default_accounts(tenant)
    ensure_hotel_accounts(tenant)

    if request.method == 'POST':
        denied_perm = check_account_permission(request.user, 'can_manage_coa')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        data = request.data or {}
        name = (data.get('name') or data.get('account_name') or '').strip()
        code = (data.get('code') or data.get('account_code') or '').strip()
        if not name or not code:
            return Response({'detail': 'Code and name are required'}, status=status.HTTP_400_BAD_REQUEST)
        parent = None
        if data.get('parent_id'):
            parent = ChartOfAccount.objects.filter(id=data.get('parent_id'), tenant=tenant).first()
        is_group = bool(data.get('is_group'))
        opening = _dec(data.get('opening_balance'))
        as_of = _date(data.get('opening_balance_as_of'))
        if opening and not as_of:
            as_of = date.today()
        try:
            with transaction.atomic():
                row = ChartOfAccount.objects.create(
                    tenant=tenant,
                    account_code=code,
                    account_name=name,
                    account_type=data.get('account_type') or (parent.account_type if parent else 'asset'),
                    parent_account=parent,
                    description=data.get('description') or '',
                    is_group=is_group,
                    book='' if is_group else (data.get('book') or ''),
                    opening_balance=Decimal('0') if is_group else opening,
                    opening_balance_as_of=None if is_group else as_of,
                    # JE sync owns current_balance for openings; start at zero.
                    current_balance=Decimal('0'),
                    is_active=data.get('is_active', True) in (True, 'true', '1', 1, 'on'),
                )
                if not is_group:
                    sync_account_opening(row, user=request.user, previous_opening=Decimal('0'))
                    row.refresh_from_db()
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        except IntegrityError:
            return Response({'detail': 'Account code already exists for this property'}, status=400)
        return Response(serialize_account(row), status=status.HTTP_201_CREATED)

    group_only = request.query_params.get('groups') == '1'
    leaves_only = request.query_params.get('leaves') == '1'
    search = (request.query_params.get('search') or '').strip()
    qs = ChartOfAccount.objects.filter(tenant=tenant)
    if group_only:
        qs = qs.filter(is_group=True)
    if leaves_only:
        qs = qs.filter(is_group=False)
    if search:
        qs = qs.filter(Q(account_code__icontains=search) | Q(account_name__icontains=search))
        return Response({'accounts': [serialize_account(row) for row in qs.order_by('account_code')]})

    rows = list(qs.order_by('account_code'))
    children_map = {}
    for row in rows:
        children_map.setdefault(row.parent_account_id, []).append(row)
    roots = [row for row in rows if row.parent_account_id is None]
    return Response({
        'accounts': [serialize_account(row, True, children_map) for row in roots],
        'flat': [serialize_account(row) for row in rows],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def erp_defaults(request):
    """FSERP-style recommended accounts for form auto-suggest."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(erp_defaults_payload(tenant))


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def account_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = ChartOfAccount.objects.get(id=pk, tenant=tenant)
    except ChartOfAccount.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        denied_perm = check_account_permission(request.user, 'can_manage_coa')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        if row.transactions.exists() or row.sub_accounts.exists():
            return Response({'detail': 'Cannot delete an account that has transactions or children'}, status=400)
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'PATCH':
        denied_perm = check_account_permission(request.user, 'can_manage_coa')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        data = request.data or {}
        previous_opening = row.opening_balance or Decimal('0')
        had_journal = bool(row.opening_balance_journal_id)
        opening_changed = False
        if data.get('name') or data.get('account_name'):
            row.account_name = data.get('name') or data.get('account_name')
        if data.get('code') or data.get('account_code'):
            row.account_code = data.get('code') or data.get('account_code')
        if data.get('account_type'):
            row.account_type = data['account_type']
        if 'parent_id' in data:
            row.parent_account = ChartOfAccount.objects.filter(id=data.get('parent_id'), tenant=tenant).first()
        if 'description' in data:
            row.description = data.get('description') or ''
        if 'is_group' in data:
            row.is_group = bool(data.get('is_group'))
        if 'book' in data:
            row.book = data.get('book') or ''
        if 'opening_balance' in data:
            row.opening_balance = _dec(data.get('opening_balance'))
            opening_changed = True
        if 'opening_balance_as_of' in data:
            row.opening_balance_as_of = _date(data.get('opening_balance_as_of'))
            opening_changed = True
        if 'is_active' in data:
            row.is_active = data.get('is_active') in (True, 'true', '1', 1, 'on')
        if opening_changed and row.opening_balance and not row.opening_balance_as_of:
            row.opening_balance_as_of = date.today()
        try:
            with transaction.atomic():
                row.save()
                if opening_changed and not row.is_group:
                    sync_account_opening(
                        row,
                        user=request.user,
                        previous_opening=None if had_journal else previous_opening,
                    )
                    row.refresh_from_db()
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        except IntegrityError:
            return Response({'detail': 'Account code already exists for this property'}, status=400)
        return Response(serialize_account(row))
    return Response(serialize_account(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vouchers(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    ensure_default_accounts(tenant)
    ensure_hotel_accounts(tenant)

    if request.method == 'POST':
        denied_perm = check_account_permission(request.user, 'can_post_vouchers')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        data = request.data or {}
        voucher_type = (data.get('voucher_type') or 'journal').replace('-', '_')
        if voucher_type not in VOUCHER_PREFIX:
            return Response({'detail': 'Unknown voucher type'}, status=400)
        entry_date = _date(data.get('date') or data.get('entry_date')) or date.today()
        lines = list(data.get('lines') or [])
        book = None
        side = None
        if voucher_type == 'cash_payment':
            book, side = 'cash', 'credit'
        elif voucher_type == 'bank_payment':
            book, side = 'bank', 'credit'
        elif voucher_type == 'cash_receipt':
            book, side = 'cash', 'debit'
        elif voucher_type == 'bank_receipt':
            book, side = 'bank', 'debit'
        if book:
            book_acc = _book_account(tenant, book)
            if not book_acc:
                return Response({'detail': f'Create a {book} account first (Head of Account)'}, status=400)
            other_total = sum(_dec(line.get('debit')) + _dec(line.get('credit')) for line in lines)
            if other_total <= 0:
                return Response({'detail': 'Enter at least one line amount'}, status=400)
            already = any(int(line.get('account_id') or 0) == book_acc.id for line in lines)
            if not already:
                lines.append({
                    'account_id': book_acc.id,
                    'debit': other_total if side == 'debit' else 0,
                    'credit': other_total if side == 'credit' else 0,
                    'description': data.get('description') or '',
                })
        try:
            with transaction.atomic():
                entry = JournalEntry.objects.create(
                    tenant=tenant,
                    entry_number=_next_number(tenant, voucher_type),
                    entry_date=entry_date,
                    voucher_type=voucher_type,
                    reference=data.get('reference') or '',
                    description=data.get('description') or '',
                    created_by=request.user,
                    is_posted=bool(data.get('post', True)),
                    posted_at=timezone.now() if data.get('post', True) else None,
                    posted_by=request.user if data.get('post', True) else None,
                )
                _apply_lines(tenant, entry, lines, posted=entry.is_posted)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_voucher(entry, include_lines=True), status=201)

    qs = JournalEntry.objects.select_related('created_by').filter(tenant=tenant)
    type_filter = request.query_params.get('type')
    if type_filter and type_filter != 'all':
        qs = qs.filter(voucher_type=type_filter.replace('-', '_'))
    search = (request.query_params.get('search') or '').strip()
    if search:
        qs = qs.filter(Q(entry_number__icontains=search) | Q(description__icontains=search))
    qs = qs.order_by('-entry_date', '-id')
    page = int(request.query_params.get('page') or 1)
    limit = int(request.query_params.get('limit') or 20)
    total = qs.count()
    start = (page - 1) * limit
    items = [serialize_voucher(row) for row in qs[start:start + limit]]
    return Response({
        'vouchers': items,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': max(1, (total + limit - 1) // limit),
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def voucher_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = JournalEntry.objects.select_related('created_by').get(id=pk, tenant=tenant)
    except JournalEntry.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'POST' and request.data.get('action') == 'post' and not row.is_posted:
        denied_perm = check_account_permission(request.user, 'can_post_vouchers')
        if denied_perm:
            return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
        try:
            with transaction.atomic():
                for line in row.transactions.select_related('account'):
                    acc = line.account
                    acc.current_balance = (acc.current_balance or 0) + _signed(acc, line.transaction_type, line.amount)
                    acc.save(update_fields=['current_balance', 'updated_at'])
                row.is_posted = True
                row.posted_at = timezone.now()
                row.posted_by = request.user
                row.save()
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
    return Response(serialize_voucher(row, include_lines=True))


def _period(request):
    start = _date(request.query_params.get('from')) or date(date.today().year, date.today().month, 1)
    end = _date(request.query_params.get('to')) or date.today()
    if end < start:
        start, end = end, start
    return start, end


def _posted_txns(tenant, start=None, end=None, account=None, book=None, account_type=None):
    qs = AccountTransaction.objects.select_related('account', 'journal_entry').filter(
        tenant=tenant,
        journal_entry__is_posted=True,
    )
    if start:
        qs = qs.filter(transaction_date__gte=start)
    if end:
        qs = qs.filter(transaction_date__lte=end)
    if account:
        qs = qs.filter(account=account)
    if book:
        qs = qs.filter(account__book=book)
    if account_type:
        qs = qs.filter(account__account_type=account_type)
    return qs.order_by('transaction_date', 'id')


def _running_rows(qs, account=None):
    items = list(qs)
    opening = Decimal('0')
    if account:
        if items:
            opening, _, _ = _balance_as_of(account, items[0].transaction_date - timedelta(days=1))
        else:
            opening = account.opening_balance or Decimal('0')
    running = opening
    rows = []
    for line in items:
        debit = line.amount if line.transaction_type == 'debit' else Decimal('0')
        credit = line.amount if line.transaction_type == 'credit' else Decimal('0')
        acc = account or line.account
        running += _signed(acc, line.transaction_type, line.amount)
        source = resolve_source(
            line.tenant,
            line.related_type,
            line.related_id,
            line.journal_entry.entry_number,
            journal_description=line.description or line.journal_entry.description,
        )
        rows.append({
            'id': line.id,
            'date': line.transaction_date.isoformat(),
            'voucher': line.journal_entry.entry_number,
            'journal_entry_id': line.journal_entry_id,
            'voucher_type': line.journal_entry.voucher_type,
            'account_id': line.account_id,
            'account': f'{line.account.account_code} {line.account.account_name}',
            'narration': line.description or line.journal_entry.description or '',
            'debit': float(debit),
            'credit': float(credit),
            'balance': float(running),
            'related_type': source.get('related_type'),
            'related_id': source.get('related_id'),
            'source_label': source.get('source_label'),
            'source_path': source.get('source_path'),
            'source_description': source.get('source_description'),
            'drill_chain': source.get('drill_chain') or [],
        })
    return float(opening), rows


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    denied_perm = check_account_permission(request.user, 'can_view_reports')
    if denied_perm:
        return Response({'detail': denied_perm}, status=status.HTTP_403_FORBIDDEN)
    ensure_default_accounts(tenant)
    ensure_hotel_accounts(tenant)
    start, end = _period(request)
    kind = kind.replace('_', '-')
    columns = ['Date', 'Voucher', 'Account', 'Narration', 'Debit', 'Credit', 'Balance', 'Source']
    rows = []
    title = kind.replace('-', ' ').title()
    summary = {}
    diggable = False

    if kind in ('cash-book', 'bank-book'):
        book = 'cash' if kind == 'cash-book' else 'bank'
        acc = _book_account(tenant, book)
        qs = _posted_txns(tenant, start, end, book=book)
        opening, rows = _running_rows(qs, account=acc)
        title = 'Cash Book' if book == 'cash' else 'Bank Book'
        summary = {'opening': opening, 'from': start.isoformat(), 'to': end.isoformat()}
    elif kind in ('general-ledger', 'group-ledger'):
        account_id = request.query_params.get('account_id')
        account = ChartOfAccount.objects.filter(id=account_id, tenant=tenant).first() if account_id else None
        if kind == 'group-ledger' and account and account.is_group:
            ids = []
            stack = [account]
            while stack:
                node = stack.pop()
                ids.append(node.id)
                stack.extend(list(node.sub_accounts.all()))
            qs = _posted_txns(tenant, start, end).filter(account_id__in=ids)
            opening, rows = _running_rows(qs)
            summary = {'opening': opening}
        elif account:
            qs = _posted_txns(tenant, start, end, account=account)
            opening, rows = _running_rows(qs, account=account)
            summary = {'opening': opening}
        else:
            diggable = True
            columns = ['Account', 'Type', 'Opening', 'Debit', 'Credit', 'Balance']
            for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False).order_by('account_code'):
                closing, debit, credit = _balance_as_of(acc, end)
                rows.append({
                    'account_id': acc.id,
                    'account': f'{acc.account_code} {acc.account_name}',
                    'account_type': acc.account_type,
                    'opening': float(acc.opening_balance or 0),
                    'debit': float(debit),
                    'credit': float(credit),
                    'balance': float(closing),
                })
    elif kind == 'opening-balance':
        diggable = True
        columns = ['Code', 'Account', 'Type', 'Opening balance', 'As of', 'Journal']
        for acc in (
            ChartOfAccount.objects.filter(tenant=tenant, is_group=False)
            .select_related('opening_balance_journal')
            .order_by('account_code')
        ):
            je = acc.opening_balance_journal
            rows.append({
                'account_id': acc.id,
                'code': acc.account_code,
                'account': acc.account_name,
                'account_type': acc.account_type,
                'opening': float(acc.opening_balance or 0),
                'as_of': acc.opening_balance_as_of.isoformat() if acc.opening_balance_as_of else None,
                'journal_entry_id': je.id if je else None,
                'voucher': je.entry_number if je else None,
            })

    elif kind == 'account-balance':
        diggable = True
        columns = ['Code', 'Account', 'Type', 'Balance']
        for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False).order_by('account_code'):
            closing, _, _ = _balance_as_of(acc, end)
            rows.append({
                'account_id': acc.id,
                'code': acc.account_code,
                'account': acc.account_name,
                'account_type': acc.account_type,
                'balance': float(closing),
            })
    elif kind == 'expense':
        diggable = True
        columns = ['Code', 'Account', 'Debit', 'Credit', 'Net expense']
        for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False, account_type='expense').order_by('account_code'):
            closing, debit, credit = _balance_as_of(acc, end)
            before, _, _ = _balance_as_of(acc, start - timedelta(days=1))
            net = closing - before
            rows.append({
                'account_id': acc.id,
                'code': acc.account_code,
                'account': acc.account_name,
                'debit': float(debit),
                'credit': float(credit),
                'net': float(net),
            })
    elif kind == 'transaction-detail':
        qs = _posted_txns(tenant, start, end)
        _, rows = _running_rows(qs)
    elif kind == 'daily-cash-sheet':
        day = end
        qs = _posted_txns(tenant, day, day, book='cash')
        receipt = sum((line.amount for line in qs if line.transaction_type == 'debit'), Decimal('0'))
        payment = sum((line.amount for line in qs if line.transaction_type == 'credit'), Decimal('0'))
        columns = ['Date', 'Voucher', 'Narration', 'Receipt', 'Payment', 'Source']
        rows = []
        for line in qs:
            source = resolve_source(
                tenant,
                line.related_type,
                line.related_id,
                line.journal_entry.entry_number,
                journal_description=line.description or line.journal_entry.description,
            )
            rows.append({
                'id': line.id,
                'date': line.transaction_date.isoformat(),
                'voucher': line.journal_entry.entry_number,
                'journal_entry_id': line.journal_entry_id,
                'narration': line.description or '',
                'receipt': float(line.amount if line.transaction_type == 'debit' else 0),
                'payment': float(line.amount if line.transaction_type == 'credit' else 0),
                'related_type': source.get('related_type'),
                'related_id': source.get('related_id'),
                'source_label': source.get('source_label'),
                'source_path': source.get('source_path'),
                'source_description': source.get('source_description'),
                'drill_chain': source.get('drill_chain') or [],
            })
        summary = {'receipts': float(receipt), 'payments': float(payment), 'net': float(receipt - payment)}
    elif kind == 'trial-balance':
        diggable = True
        columns = ['Code', 'Account', 'Debit', 'Credit']
        dr = cr = Decimal('0')
        for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False).order_by('account_code'):
            closing, _, _ = _balance_as_of(acc, end)
            if acc.account_type in NORMAL_DEBIT:
                debit = closing if closing >= 0 else Decimal('0')
                credit = -closing if closing < 0 else Decimal('0')
            else:
                credit = closing if closing >= 0 else Decimal('0')
                debit = -closing if closing < 0 else Decimal('0')
            if debit or credit:
                rows.append({
                    'account_id': acc.id,
                    'code': acc.account_code,
                    'account': acc.account_name,
                    'debit': float(debit),
                    'credit': float(credit),
                })
                dr += debit
                cr += credit
        summary = {'total_debit': float(dr), 'total_credit': float(cr)}
    elif kind == 'profit-loss':
        diggable = True
        columns = ['Account', 'Amount']
        income = expense = Decimal('0')
        for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False, account_type__in=['revenue', 'expense']).order_by('account_type', 'account_code'):
            closing, _, _ = _balance_as_of(acc, end)
            before, _, _ = _balance_as_of(acc, start - timedelta(days=1))
            net = closing - before
            rows.append({
                'account_id': acc.id,
                'account': f'{acc.account_code} {acc.account_name}',
                'account_type': acc.account_type,
                'amount': float(net),
            })
            if acc.account_type == 'revenue':
                income += net
            else:
                expense += net
        summary = {'income': float(income), 'expense': float(expense), 'net': float(income - expense)}
    elif kind == 'balance-sheet':
        diggable = True
        columns = ['Account', 'Type', 'Amount']
        totals = {'asset': Decimal('0'), 'liability': Decimal('0'), 'equity': Decimal('0')}
        income = expense = Decimal('0')
        for acc in ChartOfAccount.objects.filter(tenant=tenant, is_group=False).order_by('account_type', 'account_code'):
            closing, _, _ = _balance_as_of(acc, end)
            if acc.account_type in ('revenue', 'expense'):
                if acc.account_type == 'revenue':
                    income += closing
                else:
                    expense += closing
                continue
            rows.append({
                'account_id': acc.id,
                'account': f'{acc.account_code} {acc.account_name}',
                'account_type': acc.account_type,
                'amount': float(closing),
            })
            if acc.account_type in totals:
                totals[acc.account_type] += closing
        profit = income - expense
        rows.append({
            'account_id': None,
            'account': 'Current period surplus / (deficit)',
            'account_type': 'equity',
            'amount': float(profit),
        })
        totals['equity'] += profit
        summary = {
            'assets': float(totals['asset']),
            'liabilities': float(totals['liability']),
            'equity': float(totals['equity']),
        }
    else:
        return Response({'detail': f'Unknown report: {kind}'}, status=400)

    return Response({
        'kind': kind,
        'title': title,
        'from': start.isoformat(),
        'to': end.isoformat(),
        'columns': columns,
        'rows': rows,
        'summary': summary,
        'diggable': diggable,
        'accounts': [
            {'id': a.id, 'name': f'{a.account_code} {a.account_name}', 'is_group': a.is_group}
            for a in ChartOfAccount.objects.filter(tenant=tenant).order_by('account_code')
        ],
    })


def _bill_status(row):
    if row.balance <= 0:
        return PaymentStatus.PAID
    if row.paid_amount > 0:
        return PaymentStatus.PARTIAL
    if row.due_date and row.due_date < timezone.now().date():
        return PaymentStatus.OVERDUE
    return PaymentStatus.PENDING


def _days_overdue(row):
    if row.balance <= 0 or not row.due_date:
        return 0
    delta = (timezone.now().date() - row.due_date).days
    return delta if delta > 0 else 0


def _serialize_payable(row):
    return {
        'id': row.id,
        'invoice_number': row.invoice_number,
        'vendor_name': row.vendor_name,
        'invoice_date': row.invoice_date.isoformat() if row.invoice_date else '',
        'due_date': row.due_date.isoformat() if row.due_date else '',
        'total_amount': float(row.amount),
        'paid_amount': float(row.paid_amount),
        'balance': float(row.balance),
        'status': row.status,
        'days_overdue': _days_overdue(row),
        'name': f'{row.invoice_number} — {row.vendor_name}',
    }


def _serialize_receivable(row):
    return {
        'id': row.id,
        'invoice_number': row.invoice_number,
        'customer_name': row.customer_name,
        'invoice_date': row.invoice_date.isoformat() if row.invoice_date else '',
        'due_date': row.due_date.isoformat() if row.due_date else '',
        'total_amount': float(row.amount),
        'paid_amount': float(row.paid_amount),
        'balance': float(row.balance),
        'status': row.status,
        'days_overdue': _days_overdue(row),
        'name': f'{row.invoice_number} — {row.customer_name}',
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payable(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        vendor = (data.get('vendor_name') or '').strip()
        amount = _dec(data.get('amount') or data.get('total_amount'))
        if not vendor or amount <= 0:
            return Response({'detail': 'Vendor and amount are required'}, status=400)
        count = AccountsPayable.objects.filter(tenant=tenant).count() + 1
        inv_date = _date(data.get('invoice_date')) or timezone.now().date()
        due = _date(data.get('due_date')) or inv_date
        try:
            with transaction.atomic():
                expense = None
                if data.get('expense_account_id'):
                    expense = ChartOfAccount.objects.filter(
                        tenant=tenant, id=data.get('expense_account_id'), is_group=False
                    ).first()
                row = AccountsPayable.objects.create(
                    tenant=tenant,
                    invoice_number=(data.get('invoice_number') or '').strip() or f'AP-{tenant.id}-{count:05d}',
                    vendor_name=vendor,
                    vendor_id=int(data['vendor_id']) if data.get('vendor_id') not in (None, '') else None,
                    invoice_date=inv_date,
                    due_date=due,
                    amount=amount,
                    paid_amount=0,
                    balance=amount,
                    status=PaymentStatus.PENDING,
                    notes=data.get('notes') or '',
                    expense_account=expense,
                    created_by=request.user,
                )
                post_ap_bill(row, user=request.user)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(_serialize_payable(row), status=201)
    qs = AccountsPayable.objects.filter(tenant=tenant).order_by('-id')
    items = [_serialize_payable(row) for row in qs[:200]]
    ensure_hotel_accounts(tenant)
    leaves = ChartOfAccount.objects.filter(tenant=tenant, is_group=False, is_active=True).order_by('account_code')
    return Response({
        'payables': items,
        'items': items,
        'options': {
            'expense_accounts': [
                {'id': a.id, 'name': f'{a.account_code} {a.account_name}'}
                for a in leaves.filter(account_type='expense')
            ],
            'accounts': [{'id': a.id, 'name': f'{a.account_code} {a.account_name}'} for a in leaves],
        },
        'suggestions': erp_defaults_payload(tenant).get('suggestions') or {},
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def receivable(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        customer = (data.get('customer_name') or '').strip()
        amount = _dec(data.get('amount') or data.get('total_amount'))
        if not customer or amount <= 0:
            return Response({'detail': 'Customer and amount are required'}, status=400)
        count = AccountsReceivable.objects.filter(tenant=tenant).count() + 1
        inv_date = _date(data.get('invoice_date')) or timezone.now().date()
        due = _date(data.get('due_date')) or inv_date
        try:
            with transaction.atomic():
                revenue = None
                if data.get('revenue_account_id'):
                    revenue = ChartOfAccount.objects.filter(
                        tenant=tenant, id=data.get('revenue_account_id'), is_group=False
                    ).first()
                row = AccountsReceivable.objects.create(
                    tenant=tenant,
                    invoice_number=(data.get('invoice_number') or '').strip() or f'AR-{tenant.id}-{count:05d}',
                    customer_name=customer,
                    customer_id=int(data['customer_id']) if data.get('customer_id') not in (None, '') else None,
                    invoice_date=inv_date,
                    due_date=due,
                    amount=amount,
                    paid_amount=0,
                    balance=amount,
                    status=PaymentStatus.PENDING,
                    notes=data.get('notes') or '',
                    related_type=(data.get('related_type') or data.get('party_type') or '').strip() or None,
                    related_id=int(data['related_id']) if data.get('related_id') not in (None, '') else None,
                    revenue_account=revenue,
                    created_by=request.user,
                )
                post_ar_invoice(row, user=request.user)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(_serialize_receivable(row), status=201)
    qs = AccountsReceivable.objects.filter(tenant=tenant).order_by('-id')
    items = [_serialize_receivable(row) for row in qs[:200]]
    ensure_hotel_accounts(tenant)
    leaves = ChartOfAccount.objects.filter(tenant=tenant, is_group=False, is_active=True).order_by('account_code')
    return Response({
        'receivables': items,
        'items': items,
        'options': {
            'revenue_accounts': [
                {'id': a.id, 'name': f'{a.account_code} {a.account_name}'}
                for a in leaves.filter(account_type='revenue')
            ],
            'accounts': [{'id': a.id, 'name': f'{a.account_code} {a.account_name}'} for a in leaves],
        },
        'suggestions': erp_defaults_payload(tenant).get('suggestions') or {},
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payable_payments(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    open_bills = AccountsPayable.objects.filter(tenant=tenant).exclude(status=PaymentStatus.PAID).order_by('-id')
    if request.method == 'POST':
        data = request.data or {}
        bill = AccountsPayable.objects.filter(tenant=tenant, id=data.get('payable_id') or data.get('invoice_id')).first()
        amount = _dec(data.get('amount'))
        if not bill or amount <= 0:
            return Response({'detail': 'Open invoice and amount are required'}, status=400)
        if amount > bill.balance:
            amount = bill.balance
        try:
            with transaction.atomic():
                settle = None
                if data.get('settlement_account_id'):
                    settle = ChartOfAccount.objects.filter(
                        tenant=tenant, id=data.get('settlement_account_id'), is_group=False
                    ).first()
                pay = APPayment.objects.create(
                    accounts_payable=bill,
                    payment_date=_date(data.get('payment_date')) or timezone.now().date(),
                    amount=amount,
                    payment_method=(data.get('payment_method') or data.get('method') or 'cash'),
                    reference=data.get('reference') or '',
                    notes=data.get('notes') or '',
                    created_by=request.user,
                )
                bill.paid_amount = (bill.paid_amount or 0) + amount
                bill.balance = (bill.amount or 0) - bill.paid_amount
                bill.status = _bill_status(bill)
                bill.save(update_fields=['paid_amount', 'balance', 'status', 'updated_at'])
                post_ap_payment(pay, user=request.user, settlement=settle)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'id': pay.id, 'amount': float(pay.amount), 'balance': float(bill.balance)}, status=201)
    items = [
        {
            'id': p.id,
            'invoice_number': p.accounts_payable.invoice_number,
            'vendor_name': p.accounts_payable.vendor_name,
            'payment_date': p.payment_date.isoformat() if p.payment_date else '',
            'amount': float(p.amount),
            'method': p.payment_method or '',
            'reference': p.reference or '',
        }
        for p in APPayment.objects.filter(accounts_payable__tenant=tenant).select_related('accounts_payable').order_by('-id')[:300]
    ]
    leaves = ChartOfAccount.objects.filter(tenant=tenant, is_group=False, is_active=True).order_by('account_code')
    return Response({
        'items': items,
        'options': {
            'invoices': [{'id': b.id, 'name': f'{b.invoice_number} · due {float(b.balance):.2f}'} for b in open_bills],
            'accounts': [{'id': a.id, 'name': f'{a.account_code} {a.account_name}'} for a in leaves],
            'settlement_accounts': [
                {'id': a.id, 'name': f'{a.account_code} {a.account_name}'}
                for a in leaves.filter(book__in=['cash', 'bank'])
            ],
        },
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def receivable_payments(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    open_bills = AccountsReceivable.objects.filter(tenant=tenant).exclude(status=PaymentStatus.PAID).order_by('-id')
    if request.method == 'POST':
        data = request.data or {}
        bill = AccountsReceivable.objects.filter(tenant=tenant, id=data.get('receivable_id') or data.get('invoice_id')).first()
        amount = _dec(data.get('amount'))
        if not bill or amount <= 0:
            return Response({'detail': 'Open invoice and amount are required'}, status=400)
        if amount > bill.balance:
            amount = bill.balance
        try:
            with transaction.atomic():
                settle = None
                if data.get('settlement_account_id'):
                    settle = ChartOfAccount.objects.filter(
                        tenant=tenant, id=data.get('settlement_account_id'), is_group=False
                    ).first()
                pay = ARPayment.objects.create(
                    accounts_receivable=bill,
                    payment_date=_date(data.get('payment_date')) or timezone.now().date(),
                    amount=amount,
                    payment_method=(data.get('payment_method') or data.get('method') or 'cash'),
                    reference=data.get('reference') or '',
                    notes=data.get('notes') or '',
                    created_by=request.user,
                )
                bill.paid_amount = (bill.paid_amount or 0) + amount
                bill.balance = (bill.amount or 0) - bill.paid_amount
                bill.status = _bill_status(bill)
                bill.save(update_fields=['paid_amount', 'balance', 'status', 'updated_at'])
                post_ar_payment(pay, user=request.user, settlement=settle)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'id': pay.id, 'amount': float(pay.amount), 'balance': float(bill.balance)}, status=201)
    items = [
        {
            'id': p.id,
            'invoice_number': p.accounts_receivable.invoice_number,
            'customer_name': p.accounts_receivable.customer_name,
            'payment_date': p.payment_date.isoformat() if p.payment_date else '',
            'amount': float(p.amount),
            'method': p.payment_method or '',
            'reference': p.reference or '',
        }
        for p in ARPayment.objects.filter(accounts_receivable__tenant=tenant).select_related('accounts_receivable').order_by('-id')[:300]
    ]
    leaves = ChartOfAccount.objects.filter(tenant=tenant, is_group=False, is_active=True).order_by('account_code')
    return Response({
        'items': items,
        'options': {
            'invoices': [{'id': b.id, 'name': f'{b.invoice_number} · due {float(b.balance):.2f}'} for b in open_bills],
            'accounts': [{'id': a.id, 'name': f'{a.account_code} {a.account_name}'} for a in leaves],
            'settlement_accounts': [
                {'id': a.id, 'name': f'{a.account_code} {a.account_name}'}
                for a in leaves.filter(book__in=['cash', 'bank'])
            ],
        },
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def budgets(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    ensure_hotel_accounts(tenant)
    accounts = ChartOfAccount.objects.filter(tenant=tenant, is_group=False).order_by('account_code')
    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('name') or '').strip()
        amount = _dec(data.get('budgeted_amount') or data.get('amount'))
        account = ChartOfAccount.objects.filter(tenant=tenant, id=data.get('account_id')).first()
        start = _date(data.get('period_start'))
        end = _date(data.get('period_end'))
        if not name or not account or not start or not end or amount <= 0:
            return Response({'detail': 'Name, account, period, and amount are required'}, status=400)
        row = Budget.objects.create(
            tenant=tenant,
            name=name,
            description=data.get('description') or data.get('notes') or '',
            account=account,
            period_start=start,
            period_end=end,
            budgeted_amount=amount,
            actual_amount=0,
            variance=amount,
            created_by=request.user,
        )
        refresh_budget_actual(row)
        return Response({
            'id': row.id,
            'name': row.name,
            'actual_amount': float(row.actual_amount),
            'variance': float(row.variance),
        }, status=201)
    refresh_tenant_budgets(tenant)
    items = [
        {
            'id': row.id,
            'name': row.name,
            'account_name': f'{row.account.account_code} {row.account.account_name}',
            'period_start': row.period_start.isoformat(),
            'period_end': row.period_end.isoformat(),
            'budgeted_amount': float(row.budgeted_amount),
            'actual_amount': float(row.actual_amount),
            'variance': float(row.variance),
            'is_active': row.is_active,
        }
        for row in Budget.objects.filter(tenant=tenant).select_related('account').order_by('-period_start', '-id')[:300]
    ]
    return Response({
        'items': items,
        'budgets': items,
        'options': {'accounts': [{'id': a.id, 'name': f'{a.account_code} {a.account_name}'} for a in accounts]},
    })
