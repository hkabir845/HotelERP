"""Party subsidiary ledgers — balances reconcile to control GL accounts."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from api.models import ChartOfAccount, PartyAccount, PartyLedgerEntry, PartyType
from api.services.hotel_coa import HotelCoaCode, ensure_hotel_coa, resolve_account

TWOPLACES = Decimal('0.01')

# Party type → default control COA suffix
CONTROL_BY_TYPE = {
    PartyType.GUEST: HotelCoaCode.AR,
    PartyType.CUSTOMER: HotelCoaCode.AR_CORPORATE,
    PartyType.COMPANY: HotelCoaCode.AR_CORPORATE,
    PartyType.VENDOR: HotelCoaCode.AP,
    PartyType.SUPPLIER: HotelCoaCode.AP,
    PartyType.EMPLOYEE: HotelCoaCode.SALARY_PAYABLE,
    PartyType.LOAN_COUNTERPARTY: HotelCoaCode.LOAN_RECEIVABLE,
    PartyType.OTHER: HotelCoaCode.AR,
}

# Control accounts where positive party balance = debit (asset / receivable)
DEBIT_NORMAL_CONTROLS = {
    HotelCoaCode.AR,
    HotelCoaCode.AR_CORPORATE,
    HotelCoaCode.LOAN_RECEIVABLE,
    HotelCoaCode.LOAN_INT_RECV,
}


def _q(v) -> Decimal:
    return Decimal(str(v or 0)).quantize(TWOPLACES, ROUND_HALF_UP)


def _code_prefix(party_type: str) -> str:
    return {
        PartyType.GUEST: 'G',
        PartyType.CUSTOMER: 'C',
        PartyType.COMPANY: 'CO',
        PartyType.VENDOR: 'V',
        PartyType.SUPPLIER: 'S',
        PartyType.EMPLOYEE: 'E',
        PartyType.LOAN_COUNTERPARTY: 'L',
        PartyType.OTHER: 'P',
    }.get(party_type, 'P')


def default_control_code(party_type: str, *, loan_payable: bool = False) -> str:
    if party_type == PartyType.LOAN_COUNTERPARTY and loan_payable:
        return HotelCoaCode.LOAN_PAYABLE
    return CONTROL_BY_TYPE.get(party_type, HotelCoaCode.AR)


def control_is_debit_normal(control: ChartOfAccount) -> bool:
    code = (control.account_code or '')[-4:]
    if control.account_type in ('asset', 'expense'):
        return True
    if code in DEBIT_NORMAL_CONTROLS:
        return True
    return False


@transaction.atomic
def get_or_create_party(
    tenant,
    party_type: str,
    name: str,
    *,
    party_id: int | None = None,
    control_code: str | None = None,
    loan_payable: bool = False,
) -> PartyAccount:
    """Find or create a party account under the appropriate control GL."""
    ensure_hotel_coa(tenant)
    party_type = (party_type or PartyType.OTHER).strip().lower()
    name = (name or '').strip() or 'Unnamed party'
    if party_id:
        existing = PartyAccount.objects.filter(
            tenant=tenant, party_type=party_type, party_id=party_id, is_active=True,
        ).select_related('control_account').first()
        if existing:
            if existing.name != name:
                existing.name = name
                existing.save(update_fields=['name', 'updated_at'])
            return existing

    # Match by name under same type when no party_id
    if not party_id:
        existing = PartyAccount.objects.filter(
            tenant=tenant, party_type=party_type, name__iexact=name, is_active=True,
        ).select_related('control_account').first()
        if existing:
            return existing

    suffix = control_code or default_control_code(party_type, loan_payable=loan_payable)
    control = resolve_account(tenant, suffix)
    if not control:
        raise ValueError(f'Control account {suffix} missing — seed Chart of Accounts first')

    prefix = _code_prefix(party_type)
    if party_id:
        code = f'{prefix}-{party_id}'
    else:
        n = PartyAccount.objects.filter(tenant=tenant, party_type=party_type).count() + 1
        code = f'{prefix}-X{n:05d}'
        # Ensure unique
        while PartyAccount.objects.filter(tenant=tenant, code=code).exists():
            n += 1
            code = f'{prefix}-X{n:05d}'

    party, _ = PartyAccount.objects.get_or_create(
        tenant=tenant,
        code=code,
        defaults={
            'party_type': party_type,
            'party_id': party_id,
            'name': name,
            'control_account': control,
            'opening_balance': Decimal('0'),
            'current_balance': Decimal('0'),
            'is_active': True,
        },
    )
    if party.name != name:
        party.name = name
        party.save(update_fields=['name', 'updated_at'])
    return party


@transaction.atomic
def post_party_entry(
    party: PartyAccount,
    entry_date,
    *,
    debit=0,
    credit=0,
    narration='',
    journal_entry=None,
    related_type=None,
    related_id=None,
) -> PartyLedgerEntry | None:
    """Post a debit/credit to the party subledger and update running balance."""
    debit = _q(debit)
    credit = _q(credit)
    if debit and credit:
        raise ValueError('Party entry cannot have both debit and credit')
    if not debit and not credit:
        return None

    # Idempotent: same journal + related already posted
    if journal_entry and related_type and related_id is not None:
        exists = PartyLedgerEntry.objects.filter(
            party_account=party,
            journal_entry=journal_entry,
            related_type=related_type,
            related_id=related_id,
        ).exists()
        if exists:
            return None

    debit_normal = control_is_debit_normal(party.control_account)
    delta = (debit - credit) if debit_normal else (credit - debit)
    party.current_balance = _q(party.current_balance) + delta
    party.save(update_fields=['current_balance', 'updated_at'])

    return PartyLedgerEntry.objects.create(
        tenant=party.tenant,
        party_account=party,
        entry_date=entry_date or timezone.now().date(),
        debit=debit,
        credit=credit,
        balance_after=party.current_balance,
        narration=narration or '',
        journal_entry=journal_entry,
        related_type=related_type,
        related_id=related_id,
    )


@transaction.atomic
def sync_party_opening(party: PartyAccount) -> PartyAccount:
    """Apply opening as a one-time subledger entry (not a second GL JE)."""
    # Clear prior opening rows
    PartyLedgerEntry.objects.filter(
        party_account=party, related_type='party_opening',
    ).delete()
    # Rebuild balance from remaining entries + new opening
    rest = PartyLedgerEntry.objects.filter(party_account=party).aggregate(
        d=Sum('debit'), c=Sum('credit'),
    )
    debit_total = _q(rest['d'])
    credit_total = _q(rest['c'])
    debit_normal = control_is_debit_normal(party.control_account)
    mov = (debit_total - credit_total) if debit_normal else (credit_total - debit_total)

    amount = _q(party.opening_balance)
    as_of = party.opening_balance_as_of or date.today()
    if amount == 0:
        party.opening_balance_as_of = None
        party.current_balance = mov
        party.save(update_fields=['opening_balance', 'opening_balance_as_of', 'current_balance', 'updated_at'])
        return party

    party.opening_balance_as_of = as_of
    if debit_normal:
        debit, credit = (amount if amount > 0 else 0), (abs(amount) if amount < 0 else 0)
    else:
        credit, debit = (amount if amount > 0 else 0), (abs(amount) if amount < 0 else 0)

    party.current_balance = mov  # reset before post adds opening
    party.save(update_fields=['opening_balance_as_of', 'current_balance', 'updated_at'])
    post_party_entry(
        party,
        as_of,
        debit=debit,
        credit=credit,
        narration=f'Opening balance {party.code}',
        related_type='party_opening',
        related_id=party.id,
    )
    party.refresh_from_db()
    return party


def party_aging(tenant, *, party_type: str | None = None, as_of: date | None = None):
    """
    Aging from open AR invoices / AP bills matched to party accounts.
    Buckets: current, 1-30, 31-60, 61-90, 90+.
    """
    from api.models import AccountsPayable, AccountsReceivable, PaymentStatus

    as_of = as_of or timezone.now().date()
    buckets = ('current', 'days_1_30', 'days_31_60', 'days_61_90', 'days_90_plus')

    def bucket_key(due: date | None) -> str:
        if not due:
            return 'current'
        days = (as_of - due).days
        if days <= 0:
            return 'current'
        if days <= 30:
            return 'days_1_30'
        if days <= 60:
            return 'days_31_60'
        if days <= 90:
            return 'days_61_90'
        return 'days_90_plus'

    rows_map: dict[int, dict] = {}

    def ensure(party: PartyAccount):
        if party.id not in rows_map:
            rows_map[party.id] = {
                'party_account_id': party.id,
                'code': party.code,
                'name': party.name,
                'party_type': party.party_type,
                'control_account': f'{party.control_account.account_code} {party.control_account.account_name}',
                'current': 0.0,
                'days_1_30': 0.0,
                'days_31_60': 0.0,
                'days_61_90': 0.0,
                'days_90_plus': 0.0,
                'total': 0.0,
                'ledger_balance': float(party.current_balance or 0),
            }
        return rows_map[party.id]

    ar_types = {PartyType.GUEST, PartyType.CUSTOMER, PartyType.COMPANY, PartyType.OTHER}
    ap_types = {PartyType.VENDOR, PartyType.SUPPLIER}

    if not party_type or party_type in ar_types:
        for inv in AccountsReceivable.objects.filter(tenant=tenant).exclude(
            status=PaymentStatus.CANCELLED,
        ):
            bal = _q(inv.balance)
            if bal <= 0:
                continue
            party = None
            if inv.customer_id:
                party = PartyAccount.objects.filter(
                    tenant=tenant, party_type__in=ar_types, party_id=inv.customer_id,
                ).select_related('control_account').first()
            if not party:
                party = get_or_create_party(
                    tenant, PartyType.CUSTOMER, inv.customer_name, party_id=inv.customer_id,
                )
            if party_type and party.party_type != party_type:
                continue
            row = ensure(party)
            key = bucket_key(inv.due_date)
            row[key] += float(bal)
            row['total'] += float(bal)

    if not party_type or party_type in ap_types:
        for bill in AccountsPayable.objects.filter(tenant=tenant).exclude(
            status=PaymentStatus.CANCELLED,
        ):
            bal = _q(bill.balance)
            if bal <= 0:
                continue
            party = None
            if bill.vendor_id:
                party = PartyAccount.objects.filter(
                    tenant=tenant, party_type__in=ap_types, party_id=bill.vendor_id,
                ).select_related('control_account').first()
            if not party:
                party = get_or_create_party(
                    tenant, PartyType.VENDOR, bill.vendor_name, party_id=bill.vendor_id,
                )
            if party_type and party.party_type != party_type:
                continue
            row = ensure(party)
            key = bucket_key(bill.due_date)
            row[key] += float(bal)
            row['total'] += float(bal)

    rows = sorted(rows_map.values(), key=lambda r: (-r['total'], r['name']))
    totals = {b: sum(r[b] for r in rows) for b in buckets}
    totals['total'] = sum(r['total'] for r in rows)
    return rows, totals


def reconcile_control(tenant, control: ChartOfAccount, as_of: date | None = None):
    """Compare sum of party balances under a control account vs GL balance."""
    from api.models import AccountTransaction
    from django.db.models import Sum as DjSum

    parties = PartyAccount.objects.filter(tenant=tenant, control_account=control, is_active=True)
    party_sum = sum((_q(p.current_balance) for p in parties), Decimal('0'))

    qs = AccountTransaction.objects.filter(
        account=control,
        journal_entry__is_posted=True,
    )
    if as_of:
        qs = qs.filter(transaction_date__lte=as_of)
    debit = qs.filter(transaction_type='debit').aggregate(total=DjSum('amount'))['total'] or Decimal('0')
    credit = qs.filter(transaction_type='credit').aggregate(total=DjSum('amount'))['total'] or Decimal('0')
    if getattr(control, 'opening_balance_journal_id', None):
        opening = Decimal('0')
    else:
        opening = control.opening_balance or Decimal('0')
    if control.account_type in ('asset', 'expense'):
        gl_bal = opening + debit - credit
    else:
        gl_bal = opening + credit - debit

    return {
        'control_account_id': control.id,
        'control_code': control.account_code,
        'control_name': control.account_name,
        'party_total': float(party_sum),
        'gl_balance': float(gl_bal),
        'difference': float(_q(party_sum) - _q(gl_bal)),
        'party_count': parties.count(),
        'as_of': (as_of or timezone.now().date()).isoformat(),
    }
