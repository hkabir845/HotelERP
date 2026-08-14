"""Full-fledged Accounting System models."""
from django.db import models


class AccountType(models.TextChoices):
    """Account type."""

    ASSET = 'asset', 'Asset'
    LIABILITY = 'liability', 'Liability'
    EQUITY = 'equity', 'Equity'
    REVENUE = 'revenue', 'Revenue'
    EXPENSE = 'expense', 'Expense'


class TransactionType(models.TextChoices):
    """Transaction type."""

    DEBIT = 'debit', 'Debit'
    CREDIT = 'credit', 'Credit'


class PaymentStatus(models.TextChoices):
    """Payment status."""

    PENDING = 'pending', 'Pending'
    PARTIAL = 'partial', 'Partial'
    PAID = 'paid', 'Paid'
    OVERDUE = 'overdue', 'Overdue'
    CANCELLED = 'cancelled', 'Cancelled'


class ChartOfAccount(models.Model):
    """Chart of Accounts model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='chart_of_accounts',
        db_index=True,
    )

    account_code = models.CharField(max_length=50, db_index=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_accounts',
    )

    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_system_account = models.BooleanField(default=False)
    is_group = models.BooleanField(default=False)
    book = models.CharField(max_length=20, blank=True, default='')

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance_as_of = models.DateField(null=True, blank=True)
    opening_balance_journal = models.ForeignKey(
        'JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coa_opening_accounts',
    )
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'chart_of_accounts'
        unique_together = [['tenant', 'account_code']]
        indexes = [
            models.Index(fields=['tenant', 'account_code']),
        ]

    def __str__(self):
        return f"ChartOfAccount(id={self.id}, code='{self.account_code}', name='{self.account_name}')"


class JournalEntry(models.Model):
    """Journal Entry model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='journal_entries',
        db_index=True,
    )
    entry_number = models.CharField(max_length=50, unique=True, db_index=True)

    entry_date = models.DateField(db_index=True)
    voucher_type = models.CharField(max_length=30, default='journal', db_index=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries_posted',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries_created',
    )

    class Meta:
        db_table = 'journal_entries'

    def __str__(self):
        return f"JournalEntry(id={self.id}, entry_number='{self.entry_number}', date='{self.entry_date}')"


class AccountTransaction(models.Model):
    """Account Transaction model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='account_transactions',
        db_index=True,
    )

    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.CASCADE,
        related_name='transactions',
    )

    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)

    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)

    transaction_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_transactions'

    def __str__(self):
        return (
            f"AccountTransaction(id={self.id}, account_id={self.account_id}, "
            f"type='{self.transaction_type}', amount={self.amount})"
        )


class AccountsPayable(models.Model):
    """Accounts Payable model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='accounts_payable',
        db_index=True,
    )
    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)

    vendor_name = models.CharField(max_length=200)
    vendor_id = models.IntegerField(null=True, blank=True)

    invoice_date = models.DateField()
    due_date = models.DateField(db_index=True)

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    expense_account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts_payable',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts_payable_created',
    )

    class Meta:
        db_table = 'accounts_payable'

    def __str__(self):
        return (
            f"AccountsPayable(id={self.id}, invoice_number='{self.invoice_number}', "
            f"balance={self.balance})"
        )


class APPayment(models.Model):
    """Accounts Payable Payment model."""

    accounts_payable = models.ForeignKey(
        AccountsPayable,
        on_delete=models.CASCADE,
        related_name='payments',
    )

    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ap_payments_created',
    )

    class Meta:
        db_table = 'ap_payments'

    def __str__(self):
        return f"APPayment(id={self.id}, amount={self.amount}, date='{self.payment_date}')"


class AccountsReceivable(models.Model):
    """Accounts Receivable model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='accounts_receivable',
        db_index=True,
    )
    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)

    customer_name = models.CharField(max_length=200)
    customer_id = models.IntegerField(null=True, blank=True)

    invoice_date = models.DateField()
    due_date = models.DateField(db_index=True)

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)

    revenue_account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts_receivable',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts_receivable_created',
    )

    class Meta:
        db_table = 'accounts_receivable'

    def __str__(self):
        return (
            f"AccountsReceivable(id={self.id}, invoice_number='{self.invoice_number}', "
            f"balance={self.balance})"
        )


class ARPayment(models.Model):
    """Accounts Receivable Payment model."""

    accounts_receivable = models.ForeignKey(
        AccountsReceivable,
        on_delete=models.CASCADE,
        related_name='payments',
    )

    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ar_payments_created',
    )

    class Meta:
        db_table = 'ar_payments'

    def __str__(self):
        return f"ARPayment(id={self.id}, amount={self.amount}, date='{self.payment_date}')"


class Budget(models.Model):
    """Budget model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='budgets',
        db_index=True,
    )

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.CASCADE,
        related_name='budgets',
    )

    period_start = models.DateField()
    period_end = models.DateField()

    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets_created',
    )

    class Meta:
        db_table = 'budgets'

    def __str__(self):
        return f"Budget(id={self.id}, name='{self.name}', period='{self.period_start} to {self.period_end}')"


class PartyType(models.TextChoices):
    GUEST = 'guest', 'Guest'
    CUSTOMER = 'customer', 'Customer'
    COMPANY = 'company', 'Company'
    VENDOR = 'vendor', 'Vendor'
    SUPPLIER = 'supplier', 'Supplier'
    EMPLOYEE = 'employee', 'Employee'
    LOAN_COUNTERPARTY = 'loan_counterparty', 'Loan counterparty'
    OTHER = 'other', 'Other'


class PartyAccount(models.Model):
    """
    Subsidiary ledger account for a party (guest, vendor, customer, …).
    Balances should reconcile to the linked control GL account.
    """

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='party_accounts',
        db_index=True,
    )
    party_type = models.CharField(max_length=32, choices=PartyType.choices, db_index=True)
    party_id = models.IntegerField(null=True, blank=True, db_index=True)
    code = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=200)
    control_account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.PROTECT,
        related_name='party_accounts',
    )
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance_as_of = models.DateField(null=True, blank=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'party_accounts'
        unique_together = [['tenant', 'code']]
        indexes = [
            models.Index(fields=['tenant', 'party_type', 'party_id']),
            models.Index(fields=['tenant', 'control_account']),
        ]

    def __str__(self):
        return f"PartyAccount({self.code} {self.name})"


class PartyLedgerEntry(models.Model):
    """Movement on a party subsidiary ledger (mirrors GL control postings)."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='party_ledger_entries',
        db_index=True,
    )
    party_account = models.ForeignKey(
        PartyAccount,
        on_delete=models.CASCADE,
        related_name='ledger_entries',
    )
    entry_date = models.DateField(db_index=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    narration = models.TextField(blank=True, default='')
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='party_ledger_entries',
    )
    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'party_ledger_entries'
        indexes = [
            models.Index(fields=['tenant', 'party_account', 'entry_date']),
        ]

    def __str__(self):
        return f"PartyLedgerEntry(party={self.party_account_id}, date={self.entry_date})"

