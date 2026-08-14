"""Corporate / bank loan facilities (Accounts) — ported from FSERP loan module."""
from decimal import Decimal

from django.db import models


class LoanCounterparty(models.Model):
    """Bank, NBFC, vendor, customer, or other party on a corporate loan."""

    OPENING_ZERO = 'zero'
    OPENING_RECEIVABLE = 'receivable'
    OPENING_PAYABLE = 'payable'

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='loan_counterparties', db_index=True)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    role_type = models.CharField(max_length=32, default='other')
    party_kind = models.CharField(max_length=20, default='other')
    opening_balance_type = models.CharField(max_length=20, default=OPENING_ZERO)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    opening_balance_as_of = models.DateField(null=True, blank=True)
    opening_interest_applicable = models.BooleanField(default=False)
    opening_annual_interest_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    opening_principal_account = models.ForeignKey(
        'ChartOfAccount', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='loan_counterparties_opening_principal',
    )
    opening_equity_account = models.ForeignKey(
        'ChartOfAccount', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='loan_counterparties_opening_equity',
    )
    opening_balance_journal = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='loan_counterparty_openings',
    )
    phone = models.CharField(max_length=40, blank=True, default='')
    email = models.CharField(max_length=150, blank=True, default='')
    address = models.TextField(blank=True, default='')
    tax_id = models.CharField(max_length=80, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loan_counterparty'
        unique_together = [['tenant', 'code']]
        ordering = ['name']

    def __str__(self):
        return f'{self.code} — {self.name}'


class Loan(models.Model):
    """Money borrowed by the hotel (liability) or lent by the hotel (receivable)."""

    DIRECTION_BORROWED = 'borrowed'
    DIRECTION_LENT = 'lent'
    BANKING_CONVENTIONAL = 'conventional'  # Bank / conventional
    BANKING_ISLAMIC = 'islamic'
    PRODUCT_GENERAL = 'general'
    PRODUCT_INDIVIDUAL = 'individual'  # Person / private party facility
    PRODUCT_TERM_LOAN = 'term_loan'
    PRODUCT_BUSINESS_LINE = 'business_line'
    PRODUCT_ISLAMIC_FACILITY = 'islamic_facility'
    PRODUCT_ISLAMIC_DEAL = 'islamic_deal'

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='corporate_loans', db_index=True)
    loan_no = models.CharField(max_length=64)
    direction = models.CharField(max_length=16)
    status = models.CharField(max_length=24, default='draft')
    counterparty = models.ForeignKey(LoanCounterparty, on_delete=models.PROTECT, related_name='loans')
    banking_model = models.CharField(max_length=24, default=BANKING_CONVENTIONAL)
    product_type = models.CharField(max_length=32, default=PRODUCT_GENERAL)
    # With interest (or Islamic profit markup) vs principal-only / interest-free
    interest_bearing = models.BooleanField(default=True)
    parent_loan = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.PROTECT, related_name='child_loans',
    )
    deal_reference = models.CharField(max_length=64, blank=True, default='')
    title = models.CharField(max_length=200, blank=True, default='')
    agreement_no = models.CharField(max_length=120, blank=True, default='')
    principal_account = models.ForeignKey(
        'ChartOfAccount', on_delete=models.PROTECT, related_name='loans_principal',
    )
    settlement_account = models.ForeignKey(
        'ChartOfAccount', on_delete=models.PROTECT, related_name='loans_settlement',
    )
    interest_account = models.ForeignKey(
        'ChartOfAccount', null=True, blank=True, on_delete=models.SET_NULL, related_name='loans_interest',
    )
    interest_accrual_account = models.ForeignKey(
        'ChartOfAccount', null=True, blank=True, on_delete=models.SET_NULL, related_name='loans_interest_accrual',
    )
    islamic_contract_variant = models.CharField(max_length=24, blank=True, default='')
    sanction_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    outstanding_principal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_disbursed = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_repaid_principal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    annual_interest_rate = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0'))
    term_months = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loan'
        unique_together = [['tenant', 'loan_no']]
        ordering = ['-id']

    def __str__(self):
        return self.loan_no


class LoanDisbursement(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='disbursements')
    disbursement_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    reference = models.CharField(max_length=200, blank=True, default='')
    memo = models.TextField(blank=True, default='')
    journal_entry = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_disbursements',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_disbursement'
        ordering = ['-disbursement_date', '-id']


class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    repayment_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    interest_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reference = models.CharField(max_length=200, blank=True, default='')
    memo = models.TextField(blank=True, default='')
    journal_entry = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_repayments',
    )
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_journal_entry = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_repayment_reversals',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_repayment'
        ordering = ['-repayment_date', '-id']


class LoanInterestAccrual(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='interest_accruals')
    accrual_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    days_basis = models.PositiveSmallIntegerField(null=True, blank=True)
    memo = models.TextField(blank=True, default='')
    journal_entry = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_interest_accruals',
    )
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_journal_entry = models.ForeignKey(
        'JournalEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_accrual_reversals',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_interest_accrual'
        ordering = ['-accrual_date', '-id']
