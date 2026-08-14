"""Chart of Accounts opening balance as-of date → balanced JE vs Opening Balance Equity."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from api.models import ChartOfAccount, JournalEntry
from api.services.hotel_coa import HotelCoaCode, ensure_hotel_coa, resolve_account
from api.services.loan_gl import _signed, create_posted_entry

TWOPLACES = Decimal('0.01')
NORMAL_DEBIT = {'asset', 'expense'}


def _q(v) -> Decimal:
    return Decimal(str(v or 0)).quantize(TWOPLACES, ROUND_HALF_UP)


def _undo_posted_entry(entry: JournalEntry) -> None:
    """Reverse balance effects and delete a posted opening journal."""
    if not entry:
        return
    for line in entry.transactions.select_related('account').all():
        acc = line.account
        acc.current_balance = (acc.current_balance or 0) - _signed(acc, line.transaction_type, line.amount)
        acc.save(update_fields=['current_balance', 'updated_at'])
    # Clear FKs pointing at this entry before delete
    ChartOfAccount.objects.filter(opening_balance_journal=entry).update(opening_balance_journal=None)
    entry.delete()


def _opening_lines(account: ChartOfAccount, equity: ChartOfAccount, amount: Decimal):
    """Build Dr/Cr lines for a normal-side positive opening (negative flips)."""
    amt = abs(amount)
    label = f'Opening balance {account.account_code}'
    normal_debit = account.account_type in NORMAL_DEBIT
    debit_account = normal_debit if amount > 0 else (not normal_debit)
    if debit_account:
        return [(account, amt, 0, label), (equity, 0, amt, label)]
    return [(equity, amt, 0, label), (account, 0, amt, label)]


@transaction.atomic
def sync_account_opening(
    account: ChartOfAccount,
    user=None,
    *,
    previous_opening: Decimal | None = None,
) -> ChartOfAccount:
    """
    Post or clear the opening JE for a leaf COA account.

    Opening amount uses the account's normal balance side (positive = debit for
    assets/expenses, credit for liabilities/equity/revenue). Offset is Opening
    Balance Equity (3200).
    """
    if account.is_group:
        return account

    ensure_hotel_coa(account.tenant)
    equity = resolve_account(account.tenant, HotelCoaCode.OPENING_EQUITY)
    if equity and account.id == equity.id:
        raise ValueError('Cannot set an opening balance on Opening Balance Equity itself')

    had_journal = bool(account.opening_balance_journal_id)
    if account.opening_balance_journal_id:
        _undo_posted_entry(account.opening_balance_journal)
        account.opening_balance_journal = None
        account.save(update_fields=['opening_balance_journal', 'updated_at'])
    elif previous_opening is not None and _q(previous_opening) != 0:
        # Legacy field-only opening was baked into current_balance — strip before JE owns it.
        account.current_balance = _q(account.current_balance) - _q(previous_opening)
        account.save(update_fields=['current_balance', 'updated_at'])

    amount = _q(account.opening_balance)
    if amount == 0:
        account.opening_balance = Decimal('0.00')
        account.opening_balance_as_of = None
        account.opening_balance_journal = None
        account.save(update_fields=[
            'opening_balance', 'opening_balance_as_of', 'opening_balance_journal', 'updated_at',
        ])
        return account

    if not equity:
        raise ValueError('Opening Balance Equity (3200) missing — open Chart of Accounts once to seed defaults')

    as_of = account.opening_balance_as_of or date.today()
    account.opening_balance_as_of = as_of
    entry_no = f'AUTO-COA-OB-{account.id}'
    # Ensure stale entry number is free (undo may have deleted it)
    stale = JournalEntry.objects.filter(entry_number=entry_no).first()
    if stale:
        _undo_posted_entry(stale)

    lines = _opening_lines(account, equity, amount)
    entry = create_posted_entry(
        account.tenant,
        as_of,
        entry_no,
        f'Opening balance {account.account_code} {account.account_name}',
        lines,
        user=user,
        voucher_type='journal',
        related_type='coa_opening',
        related_id=account.id,
    )
    account.opening_balance_journal = entry
    account.save(update_fields=[
        'opening_balance_as_of', 'opening_balance_journal', 'updated_at',
    ])
    # Silence unused in some call paths
    _ = had_journal
    return account
