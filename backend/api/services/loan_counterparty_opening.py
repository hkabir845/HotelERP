"""Counterparty opening balance posting (FSERP loan_counterparty_opening port)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from api.models import LoanCounterparty
from api.services.loan_gl import create_posted_entry, resolve_account_by_suffix

TWOPLACES = Decimal('0.01')


def _q(v) -> Decimal:
    return Decimal(str(v or 0)).quantize(TWOPLACES, ROUND_HALF_UP)


@transaction.atomic
def sync_counterparty_opening(cp: LoanCounterparty, user=None) -> LoanCounterparty:
    """Post or clear opening JE for a loan counterparty."""
    amount = _q(cp.opening_balance)
    ob_type = (cp.opening_balance_type or LoanCounterparty.OPENING_ZERO).lower()

    # Clear previous opening if type/amount zeroed
    if ob_type == LoanCounterparty.OPENING_ZERO or amount <= 0:
        cp.opening_balance = Decimal('0.00')
        cp.opening_balance_type = LoanCounterparty.OPENING_ZERO
        if cp.opening_balance_journal_id:
            # Leave historical JE; just unlink for new sync (FSERP keeps JE history)
            cp.opening_balance_journal = None
        cp.save(update_fields=[
            'opening_balance', 'opening_balance_type', 'opening_balance_journal', 'updated_at',
        ])
        return cp

    principal = cp.opening_principal_account or (
        resolve_account_by_suffix(cp.tenant, '1160')
        if ob_type == LoanCounterparty.OPENING_RECEIVABLE
        else resolve_account_by_suffix(cp.tenant, '2410')
    )
    equity = cp.opening_equity_account or resolve_account_by_suffix(cp.tenant, '3200')
    if not principal or not equity:
        raise ValueError('Opening principal/equity accounts missing — run loan COA seed')

    cp.opening_principal_account = principal
    cp.opening_equity_account = equity
    as_of = cp.opening_balance_as_of or date.today()
    entry_no = f'AUTO-LOAN-CP-OB-{cp.id}'
    label = f'Opening balance {cp.code}'

    if ob_type == LoanCounterparty.OPENING_RECEIVABLE:
        # Dr receivable, Cr OBE
        lines = [(principal, amount, 0, label), (equity, 0, amount, label)]
    else:
        # Dr OBE, Cr payable
        lines = [(equity, amount, 0, label), (principal, 0, amount, label)]

    entry = create_posted_entry(
        cp.tenant, as_of, entry_no, f'Loan counterparty opening {cp.code}', lines, user=user,
        related_type='loan_counterparty', related_id=cp.id,
    )
    cp.opening_balance_journal = entry
    cp.save(update_fields=[
        'opening_principal_account', 'opening_equity_account', 'opening_balance_journal',
        'opening_balance_as_of', 'updated_at',
    ])
    return cp
