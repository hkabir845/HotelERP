"""Corporate loan APIs under Accounts (FSERP loan_views port, HotelERP-adapted)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    ChartOfAccount,
    Loan,
    LoanCounterparty,
    LoanDisbursement,
    LoanInterestAccrual,
    LoanRepayment,
)
from api.services.loan_counterparty_opening import sync_counterparty_opening
from api.services.loan_gl import ensure_loan_accounts, resolve_account_by_suffix
from api.services.loan_posting import (
    post_disbursement,
    post_interest_accrual,
    post_repayment,
    reverse_interest_accrual,
    reverse_repayment,
)
from api.services.loan_islamic import ISLAMIC_CONTRACT_VARIANTS, charge_label, loan_uses_islamic_terminology
from api.services.loan_schedule import amortized_schedule
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
    if hasattr(value, 'isoformat') and not isinstance(value, str):
        return value
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def _next_code(tenant, model, field, prefix):
    existing = (
        model.objects.filter(tenant=tenant, **{f'{field}__startswith': prefix})
        .order_by(f'-{field}')
        .values_list(field, flat=True)
        .first()
    )
    n = 1
    if existing:
        try:
            n = int(str(existing).rsplit('-', 1)[-1]) + 1
        except ValueError:
            n = model.objects.filter(tenant=tenant).count() + 1
    return f'{prefix}-{n:05d}'


def _cp_json(c: LoanCounterparty):
    return {
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'role_type': c.role_type,
        'party_kind': c.party_kind,
        'opening_balance_type': c.opening_balance_type,
        'opening_balance': float(c.opening_balance or 0),
        'opening_balance_as_of': c.opening_balance_as_of.isoformat() if c.opening_balance_as_of else None,
        'opening_interest_applicable': c.opening_interest_applicable,
        'opening_annual_interest_rate': float(c.opening_annual_interest_rate or 0)
        if c.opening_annual_interest_rate is not None
        else None,
        'opening_principal_account_id': c.opening_principal_account_id,
        'opening_equity_account_id': c.opening_equity_account_id,
        'opening_balance_journal_id': c.opening_balance_journal_id,
        'phone': c.phone or '',
        'email': c.email or '',
        'address': c.address or '',
        'tax_id': c.tax_id or '',
        'notes': c.notes or '',
        'is_active': c.is_active,
    }


def _loan_json(lo: Loan):
    islamic = loan_uses_islamic_terminology(lo)
    return {
        'id': lo.id,
        'loan_no': lo.loan_no,
        'direction': lo.direction,
        'status': lo.status,
        'counterparty_id': lo.counterparty_id,
        'counterparty_code': lo.counterparty.code if lo.counterparty_id else '',
        'counterparty_name': lo.counterparty.name if lo.counterparty_id else '',
        'banking_model': lo.banking_model,
        'product_type': lo.product_type,
        'interest_bearing': bool(lo.interest_bearing),
        'is_islamic_financing': islamic,
        'charge_label': charge_label(lo),
        'parent_loan_id': lo.parent_loan_id,
        'parent_loan_no': lo.parent_loan.loan_no if lo.parent_loan_id else '',
        'deal_reference': lo.deal_reference or '',
        'title': lo.title or '',
        'agreement_no': lo.agreement_no or '',
        'principal_account_id': lo.principal_account_id,
        'settlement_account_id': lo.settlement_account_id,
        'interest_account_id': lo.interest_account_id,
        'interest_accrual_account_id': lo.interest_accrual_account_id,
        'islamic_contract_variant': lo.islamic_contract_variant or '',
        'sanction_amount': float(lo.sanction_amount or 0),
        'outstanding_principal': float(lo.outstanding_principal or 0),
        'total_disbursed': float(lo.total_disbursed or 0),
        'total_repaid_principal': float(lo.total_repaid_principal or 0),
        'start_date': lo.start_date.isoformat() if lo.start_date else None,
        'maturity_date': lo.maturity_date.isoformat() if lo.maturity_date else None,
        'annual_interest_rate': float(lo.annual_interest_rate or 0),
        'term_months': lo.term_months,
        'notes': lo.notes or '',
    }


def _disp_json(d: LoanDisbursement):
    return {
        'id': d.id,
        'loan_id': d.loan_id,
        'disbursement_date': d.disbursement_date.isoformat(),
        'amount': float(d.amount),
        'reference': d.reference or '',
        'memo': d.memo or '',
        'journal_entry_id': d.journal_entry_id,
        'journal_entry_number': d.journal_entry.entry_number if d.journal_entry_id else None,
    }


def _pmt_json(r: LoanRepayment):
    return {
        'id': r.id,
        'loan_id': r.loan_id,
        'repayment_date': r.repayment_date.isoformat(),
        'amount': float(r.amount),
        'principal_amount': float(r.principal_amount or 0),
        'interest_amount': float(r.interest_amount or 0),
        'reference': r.reference or '',
        'memo': r.memo or '',
        'journal_entry_id': r.journal_entry_id,
        'journal_entry_number': r.journal_entry.entry_number if r.journal_entry_id else None,
        'reversed_at': r.reversed_at.isoformat() if r.reversed_at else None,
        'reversal_journal_entry_id': r.reversal_journal_entry_id,
    }


def _acc_json(a: LoanInterestAccrual):
    return {
        'id': a.id,
        'loan_id': a.loan_id,
        'accrual_date': a.accrual_date.isoformat(),
        'amount': float(a.amount),
        'days_basis': a.days_basis,
        'memo': a.memo or '',
        'journal_entry_id': a.journal_entry_id,
        'journal_entry_number': a.journal_entry.entry_number if a.journal_entry_id else None,
        'reversed_at': a.reversed_at.isoformat() if a.reversed_at else None,
        'reversal_journal_entry_id': a.reversal_journal_entry_id,
    }


def _default_accounts_for_direction(tenant, direction: str):
    ensure_loan_accounts(tenant)
    if direction == Loan.DIRECTION_BORROWED:
        principal = resolve_account_by_suffix(tenant, '2410')
        interest = resolve_account_by_suffix(tenant, '6620')
        accrual = resolve_account_by_suffix(tenant, '2415')
    else:
        principal = resolve_account_by_suffix(tenant, '1160')
        interest = resolve_account_by_suffix(tenant, '4410')
        accrual = resolve_account_by_suffix(tenant, '1165')
    settlement = (
        ChartOfAccount.objects.filter(tenant=tenant, book='bank', is_group=False, is_active=True).order_by('id').first()
        or ChartOfAccount.objects.filter(tenant=tenant, book='cash', is_group=False, is_active=True).order_by('id').first()
    )
    return principal, settlement, interest, accrual


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_meta(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    ensure_loan_accounts(tenant)
    accounts = list(
        ChartOfAccount.objects.filter(tenant=tenant, is_active=True, is_group=False)
        .order_by('account_code')
        .values('id', 'account_code', 'account_name', 'account_type', 'book')
    )
    return Response({
        'directions': [
            {'value': Loan.DIRECTION_BORROWED, 'label': 'Borrowed (liability)'},
            {'value': Loan.DIRECTION_LENT, 'label': 'Lent (receivable)'},
        ],
        'statuses': ['draft', 'approved', 'active', 'closed'],
        'banking_models': [
            {'value': Loan.BANKING_CONVENTIONAL, 'label': 'Bank (conventional)'},
            {'value': Loan.BANKING_ISLAMIC, 'label': 'Islamic banking'},
        ],
        'product_types': [
            {'value': Loan.PRODUCT_GENERAL, 'label': 'General / corporate'},
            {'value': Loan.PRODUCT_INDIVIDUAL, 'label': 'Individual loan'},
            {'value': Loan.PRODUCT_TERM_LOAN, 'label': 'Term loan'},
            {'value': Loan.PRODUCT_BUSINESS_LINE, 'label': 'Business line'},
            {'value': Loan.PRODUCT_ISLAMIC_FACILITY, 'label': 'Islamic facility (limit only)'},
            {'value': Loan.PRODUCT_ISLAMIC_DEAL, 'label': 'Islamic deal (under facility)'},
        ],
        'islamic_contract_variants': [
            {'value': v, 'label': label} for v, label in ISLAMIC_CONTRACT_VARIANTS
        ],
        'interest_modes': [
            {'value': True, 'label': 'With interest / profit'},
            {'value': False, 'label': 'Without interest (principal only)'},
        ],
        'opening_types': [
            {'value': LoanCounterparty.OPENING_ZERO, 'label': 'Zero'},
            {'value': LoanCounterparty.OPENING_RECEIVABLE, 'label': 'Receivable'},
            {'value': LoanCounterparty.OPENING_PAYABLE, 'label': 'Payable'},
        ],
        'accounts': [
            {
                'id': a['id'],
                'code': a['account_code'],
                'name': a['account_name'],
                'account_type': a['account_type'],
                'book': a['book'] or '',
            }
            for a in accounts
        ],
        'defaults': {
            'borrowed': {
                'principal_account_id': getattr(resolve_account_by_suffix(tenant, '2410'), 'id', None),
                'interest_account_id': getattr(resolve_account_by_suffix(tenant, '6620'), 'id', None),
                'interest_accrual_account_id': getattr(resolve_account_by_suffix(tenant, '2415'), 'id', None),
            },
            'lent': {
                'principal_account_id': getattr(resolve_account_by_suffix(tenant, '1160'), 'id', None),
                'interest_account_id': getattr(resolve_account_by_suffix(tenant, '4410'), 'id', None),
                'interest_accrual_account_id': getattr(resolve_account_by_suffix(tenant, '1165'), 'id', None),
            },
        },
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loan_counterparties(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)

    if request.method == 'GET':
        qs = LoanCounterparty.objects.filter(tenant=tenant)
        q = (request.query_params.get('q') or '').strip()
        if q:
            qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q))
        if request.query_params.get('active') == '1':
            qs = qs.filter(is_active=True)
        return Response([_cp_json(c) for c in qs.order_by('name')])

    body = request.data or {}
    code = (body.get('code') or '').strip() or _next_code(tenant, LoanCounterparty, 'code', 'LCP')
    if LoanCounterparty.objects.filter(tenant=tenant, code=code).exists():
        return Response({'detail': 'Counterparty code already exists'}, status=status.HTTP_400_BAD_REQUEST)
    c = LoanCounterparty.objects.create(
        tenant=tenant,
        code=code,
        name=(body.get('name') or '').strip() or code,
        role_type=(body.get('role_type') or 'other').strip(),
        party_kind=(body.get('party_kind') or 'other').strip(),
        opening_balance_type=(body.get('opening_balance_type') or LoanCounterparty.OPENING_ZERO),
        opening_balance=_dec(body.get('opening_balance')),
        opening_balance_as_of=_date(body.get('opening_balance_as_of')),
        opening_interest_applicable=bool(body.get('opening_interest_applicable')),
        opening_annual_interest_rate=_dec(body.get('opening_annual_interest_rate')) if body.get('opening_annual_interest_rate') not in (None, '') else None,
        phone=(body.get('phone') or '')[:40],
        email=(body.get('email') or '')[:150],
        address=(body.get('address') or ''),
        tax_id=(body.get('tax_id') or '')[:80],
        notes=(body.get('notes') or ''),
        is_active=bool(body.get('is_active', True)),
    )
    if body.get('post_opening', True):
        try:
            sync_counterparty_opening(c, user=request.user)
            c.refresh_from_db()
        except ValueError as exc:
            return Response({'detail': str(exc), 'counterparty': _cp_json(c)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(_cp_json(c), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def loan_counterparty_detail(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    c = LoanCounterparty.objects.filter(tenant=tenant, id=pk).first()
    if not c:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(_cp_json(c))

    if request.method == 'DELETE':
        if c.loans.exists():
            return Response({'detail': 'Counterparty has loans; deactivate instead'}, status=status.HTTP_400_BAD_REQUEST)
        c.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    body = request.data or {}
    for field in ('name', 'role_type', 'party_kind', 'phone', 'email', 'address', 'tax_id', 'notes'):
        if field in body:
            setattr(c, field, body.get(field) or '')
    if 'code' in body and body.get('code'):
        code = str(body['code']).strip()
        if LoanCounterparty.objects.filter(tenant=tenant, code=code).exclude(id=c.id).exists():
            return Response({'detail': 'Code already exists'}, status=status.HTTP_400_BAD_REQUEST)
        c.code = code
    if 'is_active' in body:
        c.is_active = bool(body['is_active'])
    if 'opening_balance_type' in body:
        c.opening_balance_type = body['opening_balance_type'] or LoanCounterparty.OPENING_ZERO
    if 'opening_balance' in body:
        c.opening_balance = _dec(body.get('opening_balance'))
    if 'opening_balance_as_of' in body:
        c.opening_balance_as_of = _date(body.get('opening_balance_as_of'))
    if 'opening_interest_applicable' in body:
        c.opening_interest_applicable = bool(body['opening_interest_applicable'])
    if 'opening_annual_interest_rate' in body:
        c.opening_annual_interest_rate = (
            _dec(body.get('opening_annual_interest_rate'))
            if body.get('opening_annual_interest_rate') not in (None, '')
            else None
        )
    c.save()
    if body.get('post_opening'):
        try:
            sync_counterparty_opening(c, user=request.user)
            c.refresh_from_db()
        except ValueError as exc:
            return Response({'detail': str(exc), 'counterparty': _cp_json(c)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(_cp_json(c))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loans_list(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)

    if request.method == 'GET':
        qs = Loan.objects.filter(tenant=tenant).select_related('counterparty', 'parent_loan')
        direction = request.query_params.get('direction')
        status_f = request.query_params.get('status')
        cp = request.query_params.get('counterparty_id')
        banking = request.query_params.get('banking_model')
        product = request.query_params.get('product_type')
        interest_bearing = request.query_params.get('interest_bearing')
        q = (request.query_params.get('q') or '').strip()
        if direction:
            qs = qs.filter(direction=direction)
        if status_f:
            qs = qs.filter(status=status_f)
        if cp:
            qs = qs.filter(counterparty_id=cp)
        if banking:
            qs = qs.filter(banking_model=banking)
        if product:
            qs = qs.filter(product_type=product)
        if interest_bearing in ('0', 'false', 'False'):
            qs = qs.filter(interest_bearing=False)
        elif interest_bearing in ('1', 'true', 'True'):
            qs = qs.filter(interest_bearing=True)
        if q:
            qs = qs.filter(
                Q(loan_no__icontains=q) | Q(title__icontains=q) | Q(counterparty__name__icontains=q)
            )
        return Response([_loan_json(x) for x in qs.order_by('-id')])

    body = request.data or {}
    direction = (body.get('direction') or Loan.DIRECTION_BORROWED).strip()
    if direction not in (Loan.DIRECTION_BORROWED, Loan.DIRECTION_LENT):
        return Response({'detail': 'Invalid direction'}, status=status.HTTP_400_BAD_REQUEST)
    cp_id = body.get('counterparty_id')
    cp = LoanCounterparty.objects.filter(tenant=tenant, id=cp_id, is_active=True).first()
    if not cp:
        return Response({'detail': 'counterparty_id required'}, status=status.HTTP_400_BAD_REQUEST)

    principal, settlement, interest, accrual = _default_accounts_for_direction(tenant, direction)
    principal_id = body.get('principal_account_id') or (principal.id if principal else None)
    settlement_id = body.get('settlement_account_id') or (settlement.id if settlement else None)
    interest_id = body.get('interest_account_id') or (interest.id if interest else None)
    accrual_id = body.get('interest_accrual_account_id') or (accrual.id if accrual else None)

    for label, aid in (('principal', principal_id), ('settlement', settlement_id)):
        if not aid or not ChartOfAccount.objects.filter(tenant=tenant, id=aid, is_group=False).exists():
            return Response({'detail': f'{label}_account_id required'}, status=status.HTTP_400_BAD_REQUEST)

    loan_no = (body.get('loan_no') or '').strip() or _next_code(tenant, Loan, 'loan_no', 'LN')
    if Loan.objects.filter(tenant=tenant, loan_no=loan_no).exists():
        return Response({'detail': 'loan_no already exists'}, status=status.HTTP_400_BAD_REQUEST)

    parent = None
    product_type = (body.get('product_type') or Loan.PRODUCT_GENERAL).strip()
    banking_model = (body.get('banking_model') or Loan.BANKING_CONVENTIONAL).strip()
    if product_type in (Loan.PRODUCT_ISLAMIC_FACILITY, Loan.PRODUCT_ISLAMIC_DEAL):
        banking_model = Loan.BANKING_ISLAMIC
    if product_type == Loan.PRODUCT_ISLAMIC_DEAL:
        parent = Loan.objects.filter(
            tenant=tenant, id=body.get('parent_loan_id'), product_type=Loan.PRODUCT_ISLAMIC_FACILITY,
        ).first()
        if not parent:
            return Response(
                {'detail': 'Islamic deal requires parent Islamic facility (parent_loan_id)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    interest_bearing = body.get('interest_bearing', True)
    if isinstance(interest_bearing, str):
        interest_bearing = interest_bearing.lower() not in ('0', 'false', 'no')
    interest_bearing = bool(interest_bearing)
    rate = _dec(body.get('annual_interest_rate'))
    if not interest_bearing:
        rate = Decimal('0')

    lo = Loan.objects.create(
        tenant=tenant,
        loan_no=loan_no,
        direction=direction,
        status=(body.get('status') or 'draft'),
        counterparty=cp,
        banking_model=banking_model,
        product_type=product_type,
        interest_bearing=interest_bearing,
        parent_loan=parent,
        deal_reference=(body.get('deal_reference') or '')[:64],
        title=(body.get('title') or '')[:200],
        agreement_no=(body.get('agreement_no') or '')[:120],
        principal_account_id=principal_id,
        settlement_account_id=settlement_id,
        interest_account_id=interest_id if interest_bearing else None,
        interest_accrual_account_id=accrual_id if interest_bearing else None,
        islamic_contract_variant=(body.get('islamic_contract_variant') or '')[:24] if banking_model == Loan.BANKING_ISLAMIC else '',
        sanction_amount=_dec(body.get('sanction_amount')),
        start_date=_date(body.get('start_date')),
        maturity_date=_date(body.get('maturity_date')),
        annual_interest_rate=rate,
        term_months=int(body['term_months']) if body.get('term_months') not in (None, '') else None,
        notes=(body.get('notes') or ''),
    )
    return Response(_loan_json(lo), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def loan_detail(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty', 'parent_loan').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = _loan_json(lo)
        data['disbursements'] = [_disp_json(d) for d in lo.disbursements.select_related('journal_entry').all()]
        data['repayments'] = [_pmt_json(r) for r in lo.repayments.select_related('journal_entry').all()]
        data['interest_accruals'] = [_acc_json(a) for a in lo.interest_accruals.select_related('journal_entry').all()]
        return Response(data)

    if request.method == 'DELETE':
        if lo.disbursements.exists() or lo.repayments.exists():
            return Response({'detail': 'Loan has postings; close instead of delete'}, status=status.HTTP_400_BAD_REQUEST)
        lo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    body = request.data or {}
    for field in (
        'title', 'agreement_no', 'deal_reference', 'notes', 'islamic_contract_variant',
        'banking_model', 'product_type', 'status',
    ):
        if field in body:
            setattr(lo, field, body.get(field) or ('' if field != 'status' else lo.status))
    if 'interest_bearing' in body:
        ib = body.get('interest_bearing')
        if isinstance(ib, str):
            ib = ib.lower() not in ('0', 'false', 'no')
        lo.interest_bearing = bool(ib)
        if not lo.interest_bearing:
            lo.annual_interest_rate = Decimal('0')
    if lo.product_type in (Loan.PRODUCT_ISLAMIC_FACILITY, Loan.PRODUCT_ISLAMIC_DEAL):
        lo.banking_model = Loan.BANKING_ISLAMIC
    if 'counterparty_id' in body:
        cp = LoanCounterparty.objects.filter(tenant=tenant, id=body.get('counterparty_id')).first()
        if not cp:
            return Response({'detail': 'Invalid counterparty'}, status=status.HTTP_400_BAD_REQUEST)
        lo.counterparty = cp
    for acc_field in (
        'principal_account_id', 'settlement_account_id', 'interest_account_id', 'interest_accrual_account_id',
    ):
        if acc_field in body and body.get(acc_field):
            if not ChartOfAccount.objects.filter(tenant=tenant, id=body.get(acc_field), is_group=False).exists():
                return Response({'detail': f'Invalid {acc_field}'}, status=status.HTTP_400_BAD_REQUEST)
            setattr(lo, acc_field, body.get(acc_field))
    if 'sanction_amount' in body:
        lo.sanction_amount = _dec(body.get('sanction_amount'))
    if 'annual_interest_rate' in body:
        lo.annual_interest_rate = Decimal('0') if not lo.interest_bearing else _dec(body.get('annual_interest_rate'))
    if 'term_months' in body:
        lo.term_months = int(body['term_months']) if body.get('term_months') not in (None, '') else None
    if 'start_date' in body:
        lo.start_date = _date(body.get('start_date'))
    if 'maturity_date' in body:
        lo.maturity_date = _date(body.get('maturity_date'))
    if 'parent_loan_id' in body:
        pid = body.get('parent_loan_id')
        lo.parent_loan = Loan.objects.filter(tenant=tenant, id=pid).first() if pid else None
    lo.save()
    return Response(_loan_json(lo))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_disburse(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    body = request.data or {}
    try:
        with transaction.atomic():
            d = post_disbursement(
                lo,
                amount=body.get('amount'),
                disbursement_date=_date(body.get('disbursement_date')),
                reference=(body.get('reference') or ''),
                memo=(body.get('memo') or ''),
                user=request.user,
            )
            lo.refresh_from_db()
            return Response({'disbursement': _disp_json(d), 'loan': _loan_json(lo)}, status=status.HTTP_201_CREATED)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_repay(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    body = request.data or {}
    try:
        with transaction.atomic():
            r = post_repayment(
                lo,
                amount=body.get('amount'),
                repayment_date=_date(body.get('repayment_date')),
                principal_amount=body.get('principal_amount'),
                interest_amount=body.get('interest_amount'),
                reference=(body.get('reference') or ''),
                memo=(body.get('memo') or ''),
                user=request.user,
            )
            lo.refresh_from_db()
            return Response({'repayment': _pmt_json(r), 'loan': _loan_json(lo)}, status=status.HTTP_201_CREATED)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_repayment_reverse(request, pk: int, repayment_id: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    r = LoanRepayment.objects.filter(loan=lo, id=repayment_id).first()
    if not r:
        return Response({'detail': 'Repayment not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        reverse_repayment(r, user=request.user)
        lo.refresh_from_db()
        r.refresh_from_db()
        return Response({'repayment': _pmt_json(r), 'loan': _loan_json(lo)})
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_accrue(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    body = request.data or {}
    amount = body.get('amount')
    if amount in (None, '') and lo.outstanding_principal and lo.annual_interest_rate:
        # Simple 30/360 monthly estimate when amount omitted
        amount = (Decimal(str(lo.outstanding_principal)) * Decimal(str(lo.annual_interest_rate)) / Decimal('100') / Decimal('12'))
    try:
        a = post_interest_accrual(
            lo,
            amount=amount,
            accrual_date=_date(body.get('accrual_date')),
            days_basis=int(body['days_basis']) if body.get('days_basis') not in (None, '') else None,
            memo=(body.get('memo') or ''),
            user=request.user,
        )
        return Response({'accrual': _acc_json(a), 'loan': _loan_json(lo)}, status=status.HTTP_201_CREATED)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_accrual_reverse(request, pk: int, accrual_id: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).select_related('counterparty').first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    a = LoanInterestAccrual.objects.filter(loan=lo, id=accrual_id).first()
    if not a:
        return Response({'detail': 'Accrual not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        reverse_interest_accrual(a, user=request.user)
        a.refresh_from_db()
        return Response({'accrual': _acc_json(a), 'loan': _loan_json(lo)})
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loan_schedule(request, pk: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    lo = Loan.objects.filter(tenant=tenant, id=pk).first()
    if not lo:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    body = request.data if request.method == 'POST' else request.query_params
    principal = _dec(body.get('principal'), str(lo.sanction_amount or lo.outstanding_principal or 0))
    rate = _dec(body.get('annual_interest_rate'), str(lo.annual_interest_rate or 0))
    months = int(body.get('term_months') or lo.term_months or 0)
    start = _date(body.get('start_date')) or lo.start_date
    rows = amortized_schedule(principal, rate, months, start)
    return Response({
        'loan_id': lo.id,
        'principal': float(principal),
        'annual_interest_rate': float(rate),
        'term_months': months,
        'start_date': start.isoformat() if start else None,
        'rows': rows,
    })
