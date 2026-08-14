"""Corporate loan journal postings (FSERP loan_posting port)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from api.models import Loan, LoanDisbursement, LoanInterestAccrual, LoanRepayment
from api.services.loan_gl import create_posted_entry, resolve_account_by_suffix
from api.services.loan_islamic import charge_label

TWOPLACES = Decimal('0.01')


def _q(v) -> Decimal:
    return Decimal(str(v or 0)).quantize(TWOPLACES, ROUND_HALF_UP)


def _default_interest_account(loan: Loan):
    if loan.interest_account_id:
        return loan.interest_account
    suffix = '6620' if loan.direction == Loan.DIRECTION_BORROWED else '4410'
    return resolve_account_by_suffix(loan.tenant, suffix)


def _default_accrual_account(loan: Loan):
    if loan.interest_accrual_account_id:
        return loan.interest_accrual_account
    suffix = '2415' if loan.direction == Loan.DIRECTION_BORROWED else '1165'
    return resolve_account_by_suffix(loan.tenant, suffix)


@transaction.atomic
def post_disbursement(loan: Loan, amount, disbursement_date=None, reference='', memo='', user=None) -> LoanDisbursement:
    amount = _q(amount)
    if amount <= 0:
        raise ValueError('Disbursement amount must be positive')
    if loan.status == 'closed':
        raise ValueError('Cannot disburse a closed loan')
    if loan.product_type == Loan.PRODUCT_ISLAMIC_FACILITY:
        raise ValueError('Islamic facility is a limit only — disburse on Islamic deal rows')

    d = disbursement_date or date.today()
    disp = LoanDisbursement.objects.create(
        loan=loan,
        disbursement_date=d,
        amount=amount,
        reference=reference or '',
        memo=memo or '',
    )
    entry_no = f'AUTO-LOAN-DISP-{disp.id}'
    if loan.direction == Loan.DIRECTION_BORROWED:
        # Dr cash/bank, Cr loan payable
        lines = [
            (loan.settlement_account, amount, 0, memo or f'Disburse {loan.loan_no}'),
            (loan.principal_account, 0, amount, memo or f'Disburse {loan.loan_no}'),
        ]
    else:
        # Dr loans receivable, Cr cash/bank
        lines = [
            (loan.principal_account, amount, 0, memo or f'Disburse {loan.loan_no}'),
            (loan.settlement_account, 0, amount, memo or f'Disburse {loan.loan_no}'),
        ]
    entry = create_posted_entry(
        loan.tenant, d, entry_no, f'Loan disbursement {loan.loan_no}', lines, user=user, voucher_type='journal',
        related_type='loan_disbursement', related_id=disp.id,
    )
    disp.journal_entry = entry
    disp.save(update_fields=['journal_entry'])

    try:
        from api.models import PartyType
        from api.services.hotel_coa import HotelCoaCode
        from api.services.party_ledger import get_or_create_party, post_party_entry
        cp = loan.counterparty
        payable = loan.direction == Loan.DIRECTION_BORROWED
        party = get_or_create_party(
            loan.tenant, PartyType.LOAN_COUNTERPARTY, cp.name,
            party_id=cp.id, loan_payable=payable,
            control_code=HotelCoaCode.LOAN_PAYABLE if payable else HotelCoaCode.LOAN_RECEIVABLE,
        )
        if payable:
            post_party_entry(party, d, credit=amount, narration=f'Disburse {loan.loan_no}',
                             journal_entry=entry, related_type='loan_disbursement', related_id=disp.id)
        else:
            post_party_entry(party, d, debit=amount, narration=f'Disburse {loan.loan_no}',
                             journal_entry=entry, related_type='loan_disbursement', related_id=disp.id)
    except Exception:
        pass

    loan.total_disbursed = _q(loan.total_disbursed) + amount
    loan.outstanding_principal = _q(loan.outstanding_principal) + amount
    if loan.status in ('draft', 'approved'):
        loan.status = 'active'
    if not loan.start_date:
        loan.start_date = d
    loan.save(update_fields=[
        'total_disbursed', 'outstanding_principal', 'status', 'start_date', 'updated_at',
    ])
    return disp


@transaction.atomic
def post_repayment(
    loan: Loan,
    amount,
    repayment_date=None,
    principal_amount=None,
    interest_amount=None,
    reference='',
    memo='',
    user=None,
) -> LoanRepayment:
    amount = _q(amount)
    if amount <= 0:
        raise ValueError('Repayment amount must be positive')
    if loan.status == 'closed':
        raise ValueError('Cannot repay a closed loan')

    d = repayment_date or date.today()
    if not loan.interest_bearing:
        # Interest-free: entire payment is principal
        if interest_amount not in (None, '', 0, '0', '0.0', '0.00') and _q(interest_amount) > 0:
            raise ValueError(f'This loan is interest-free; cannot post {charge_label(loan).lower()}')
        principal_amount = amount
        interest_amount = Decimal('0.00')
    elif principal_amount is None and interest_amount is None:
        # Apply to principal first
        principal_amount = min(amount, _q(loan.outstanding_principal))
        interest_amount = _q(amount - principal_amount)
    else:
        principal_amount = _q(principal_amount or 0)
        interest_amount = _q(interest_amount or 0)
        if _q(principal_amount + interest_amount) != amount:
            raise ValueError(f'Principal + {charge_label(loan).lower()} must equal total amount')

    if principal_amount > _q(loan.outstanding_principal):
        raise ValueError('Principal exceeds outstanding')

    interest_acc = _default_interest_account(loan)
    if interest_amount > 0 and not interest_acc:
        raise ValueError(f'{charge_label(loan)} GL account is required for that portion')

    pmt = LoanRepayment.objects.create(
        loan=loan,
        repayment_date=d,
        amount=amount,
        principal_amount=principal_amount,
        interest_amount=interest_amount,
        reference=reference or '',
        memo=memo or '',
    )
    entry_no = f'AUTO-LOAN-PMT-{pmt.id}'
    lines = []
    label = memo or f'Repayment {loan.loan_no}'
    if loan.direction == Loan.DIRECTION_BORROWED:
        # Dr payable (principal), Dr interest expense, Cr cash
        if principal_amount:
            lines.append((loan.principal_account, principal_amount, 0, label))
        if interest_amount:
            lines.append((interest_acc, interest_amount, 0, label))
        lines.append((loan.settlement_account, 0, amount, label))
    else:
        # Dr cash, Cr receivable, Cr interest income
        lines.append((loan.settlement_account, amount, 0, label))
        if principal_amount:
            lines.append((loan.principal_account, 0, principal_amount, label))
        if interest_amount:
            lines.append((interest_acc, 0, interest_amount, label))

    entry = create_posted_entry(
        loan.tenant, d, entry_no, f'Loan repayment {loan.loan_no}', lines, user=user, voucher_type='journal',
        related_type='loan_repayment', related_id=pmt.id,
    )
    pmt.journal_entry = entry
    pmt.save(update_fields=['journal_entry'])

    try:
        from api.models import PartyType
        from api.services.hotel_coa import HotelCoaCode
        from api.services.party_ledger import get_or_create_party, post_party_entry
        cp = loan.counterparty
        payable = loan.direction == Loan.DIRECTION_BORROWED
        party = get_or_create_party(
            loan.tenant, PartyType.LOAN_COUNTERPARTY, cp.name,
            party_id=cp.id, loan_payable=payable,
            control_code=HotelCoaCode.LOAN_PAYABLE if payable else HotelCoaCode.LOAN_RECEIVABLE,
        )
        # Principal portion reduces party outstanding
        if principal_amount:
            if payable:
                post_party_entry(party, d, debit=principal_amount, narration=f'Repay {loan.loan_no}',
                                 journal_entry=entry, related_type='loan_repayment', related_id=pmt.id)
            else:
                post_party_entry(party, d, credit=principal_amount, narration=f'Repay {loan.loan_no}',
                                 journal_entry=entry, related_type='loan_repayment', related_id=pmt.id)
    except Exception:
        pass

    loan.outstanding_principal = _q(loan.outstanding_principal) - principal_amount
    loan.total_repaid_principal = _q(loan.total_repaid_principal) + principal_amount
    if loan.outstanding_principal <= 0 and _q(loan.total_disbursed) > 0:
        loan.status = 'closed'
        loan.outstanding_principal = Decimal('0.00')
    loan.save(update_fields=[
        'outstanding_principal', 'total_repaid_principal', 'status', 'updated_at',
    ])
    return pmt


@transaction.atomic
def reverse_repayment(pmt: LoanRepayment, user=None) -> LoanRepayment:
    if pmt.reversed_at:
        raise ValueError('Already reversed')
    if not pmt.journal_entry_id:
        raise ValueError('No journal to reverse')
    loan = pmt.loan
    d = date.today()
    entry_no = f'AUTO-LOAN-PMT-REV-{pmt.id}'
    # Flip original lines
    from api.models import AccountTransaction
    orig = list(AccountTransaction.objects.filter(journal_entry=pmt.journal_entry).select_related('account'))
    lines = []
    for t in orig:
        if t.transaction_type == 'debit':
            lines.append((t.account, 0, t.amount, f'Reversal of {pmt.journal_entry.entry_number}'))
        else:
            lines.append((t.account, t.amount, 0, f'Reversal of {pmt.journal_entry.entry_number}'))
    entry = create_posted_entry(
        loan.tenant, d, entry_no, f'Reverse repayment {loan.loan_no}', lines, user=user,
        related_type='loan_repayment', related_id=pmt.id,
    )
    pmt.reversed_at = timezone.now()
    pmt.reversal_journal_entry = entry
    pmt.save(update_fields=['reversed_at', 'reversal_journal_entry'])

    loan.outstanding_principal = _q(loan.outstanding_principal) + _q(pmt.principal_amount)
    loan.total_repaid_principal = _q(loan.total_repaid_principal) - _q(pmt.principal_amount)
    if loan.status == 'closed':
        loan.status = 'active'
    loan.save(update_fields=['outstanding_principal', 'total_repaid_principal', 'status', 'updated_at'])
    return pmt


@transaction.atomic
def post_interest_accrual(loan: Loan, amount, accrual_date=None, days_basis=None, memo='', user=None) -> LoanInterestAccrual:
    amount = _q(amount)
    if amount <= 0:
        raise ValueError('Accrual amount must be positive')
    if not loan.interest_bearing:
        raise ValueError(f'Cannot accrue {charge_label(loan).lower()} on an interest-free loan')
    if loan.product_type == Loan.PRODUCT_ISLAMIC_FACILITY:
        raise ValueError('Post accruals on Islamic deal rows, not on the facility limit')
    interest_acc = _default_interest_account(loan)
    accrual_acc = _default_accrual_account(loan)
    if not interest_acc or not accrual_acc:
        raise ValueError('Interest and accrual accounts are required')

    d = accrual_date or date.today()
    row = LoanInterestAccrual.objects.create(
        loan=loan,
        accrual_date=d,
        amount=amount,
        days_basis=days_basis,
        memo=memo or '',
    )
    entry_no = f'AUTO-LOAN-ACC-{row.id}'
    label = memo or f'Interest accrual {loan.loan_no}'
    if loan.direction == Loan.DIRECTION_BORROWED:
        # Dr interest expense, Cr accrued interest payable
        lines = [(interest_acc, amount, 0, label), (accrual_acc, 0, amount, label)]
    else:
        # Dr accrued interest receivable, Cr interest income
        lines = [(accrual_acc, amount, 0, label), (interest_acc, 0, amount, label)]
    entry = create_posted_entry(
        loan.tenant, d, entry_no, f'Loan interest accrual {loan.loan_no}', lines, user=user,
        related_type='loan_accrual', related_id=row.id,
    )
    row.journal_entry = entry
    row.save(update_fields=['journal_entry'])
    return row


@transaction.atomic
def reverse_interest_accrual(row: LoanInterestAccrual, user=None) -> LoanInterestAccrual:
    if row.reversed_at:
        raise ValueError('Already reversed')
    if not row.journal_entry_id:
        raise ValueError('No journal to reverse')
    from api.models import AccountTransaction
    loan = row.loan
    d = date.today()
    entry_no = f'AUTO-LOAN-ACC-REV-{row.id}'
    orig = list(AccountTransaction.objects.filter(journal_entry=row.journal_entry).select_related('account'))
    lines = []
    for t in orig:
        if t.transaction_type == 'debit':
            lines.append((t.account, 0, t.amount, f'Reversal of {row.journal_entry.entry_number}'))
        else:
            lines.append((t.account, t.amount, 0, f'Reversal of {row.journal_entry.entry_number}'))
    entry = create_posted_entry(
        loan.tenant, d, entry_no, f'Reverse accrual {loan.loan_no}', lines, user=user,
        related_type='loan_accrual', related_id=row.id,
    )
    row.reversed_at = timezone.now()
    row.reversal_journal_entry = entry
    row.save(update_fields=['reversed_at', 'reversal_journal_entry'])
    return row
