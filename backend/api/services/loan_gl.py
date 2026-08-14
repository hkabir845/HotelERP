"""Shared GL helper for corporate loan postings."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from api.models import AccountTransaction, ChartOfAccount, JournalEntry

NORMAL_DEBIT = {'asset', 'expense'}

LOAN_COA_SPECS = [
    # code, name, type, is_group, book, parent_code
    ('1150', 'Loans & Advances', 'asset', True, '', '1100'),
    ('1160', 'Loans Receivable — Principal', 'asset', False, 'loan_recv', '1150'),
    ('1165', 'Accrued Interest Receivable', 'asset', False, 'loan_acc_a', '1150'),
    ('2400', 'Loans Payable', 'liability', True, '', '2000'),
    ('2410', 'Loans Payable — Principal', 'liability', False, 'loan_pay', '2400'),
    ('2415', 'Accrued Interest Payable', 'liability', False, 'loan_acc_l', '2400'),
    ('3200', 'Opening Balance Equity', 'equity', False, 'obe', '3000'),
    ('4410', 'Interest Income — Loans', 'revenue', False, 'loan_int_in', '4000'),
    ('6620', 'Interest Expense — Loan Borrowings', 'expense', False, 'loan_int_ex', '5000'),
]


def _signed(account, txn_type, amount):
    amount = Decimal(str(amount or 0))
    if account.account_type in NORMAL_DEBIT:
        return amount if txn_type == 'debit' else -amount
    return amount if txn_type == 'credit' else -amount


def ensure_loan_accounts(tenant):
    """Ensure hotel chart (includes loan lines) exists for the tenant."""
    from api.services.hotel_coa import ensure_hotel_coa

    return ensure_hotel_coa(tenant)


def resolve_account_by_suffix(tenant, suffix: str):
    from api.services.hotel_coa import resolve_account

    return resolve_account(tenant, suffix)


def create_posted_entry(
    tenant,
    entry_date,
    entry_number,
    description,
    lines,
    user=None,
    voucher_type='journal',
    related_type=None,
    related_id=None,
):
    """
    Create a posted balanced journal.
    lines: list of (ChartOfAccount, debit, credit, memo)
    Optional related_type / related_id link every line to a source document for report drill-down.
    """
    if JournalEntry.objects.filter(entry_number=entry_number).exists():
        return JournalEntry.objects.filter(entry_number=entry_number).first()

    prepared = []
    total_d = Decimal('0')
    total_c = Decimal('0')
    for account, debit, credit, memo in lines:
        debit = Decimal(str(debit or 0))
        credit = Decimal(str(credit or 0))
        if debit and credit:
            raise ValueError('A line cannot have both debit and credit')
        if not debit and not credit:
            continue
        if not account or account.tenant_id != tenant.id or account.is_group or not account.is_active:
            raise ValueError('Invalid GL account on loan journal')
        prepared.append((account, debit, credit, memo or ''))
        total_d += debit
        total_c += credit
    if total_d != total_c:
        raise ValueError(f'Debit {total_d} must equal credit {total_c}')
    if total_d <= 0:
        raise ValueError('Empty journal')

    with transaction.atomic():
        entry = JournalEntry.objects.create(
            tenant=tenant,
            entry_number=entry_number,
            entry_date=entry_date,
            voucher_type=voucher_type,
            reference=entry_number,
            description=description,
            total_debit=total_d,
            total_credit=total_c,
            is_posted=True,
            posted_at=timezone.now(),
            posted_by=user,
            created_by=user,
        )
        for account, debit, credit, memo in prepared:
            txn_type = 'debit' if debit else 'credit'
            amount = debit or credit
            AccountTransaction.objects.create(
                tenant=tenant,
                journal_entry=entry,
                account=account,
                transaction_type=txn_type,
                amount=amount,
                description=memo or description,
                reference=entry_number,
                related_type=related_type or None,
                related_id=related_id,
                transaction_date=entry_date,
            )
            account.current_balance = (account.current_balance or 0) + _signed(account, txn_type, amount)
            account.save(update_fields=['current_balance', 'updated_at'])
    return entry
