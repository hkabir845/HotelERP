"""F&B configuration, POS customers, and outlet expenses."""
from django.db import models


class FnbNamed(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name='{self.name}')"


class RevenueCenter(FnbNamed):
    class Meta:
        db_table = 'fnb_revenue_centers'


class FnbCategory(FnbNamed):
    class Meta:
        db_table = 'fnb_categories'


class FnbSubCategory(FnbNamed):
    category = models.ForeignKey(
        FnbCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
    )

    class Meta:
        db_table = 'fnb_subcategories'


class FnbUnit(FnbNamed):
    class Meta:
        db_table = 'fnb_units'


class FnbToken(FnbNamed):
    class Meta:
        db_table = 'fnb_tokens'


class ServeBy(FnbNamed):
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'fnb_serve_by'


class TakeAwayAgent(FnbNamed):
    phone = models.CharField(max_length=50, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'fnb_take_away_agents'


class PosCustomer(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='pos_customers',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'pos_customers'

    def __str__(self):
        return f"PosCustomer(id={self.id}, name='{self.name}')"


class PosDueReceive(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='pos_due_receives',
        db_index=True,
    )
    customer = models.ForeignKey(
        PosCustomer,
        on_delete=models.CASCADE,
        related_name='due_receives',
    )
    receive_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, default='cash')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_due_receives',
    )

    class Meta:
        db_table = 'pos_due_receives'


class FnbExpenseCategory(FnbNamed):
    class Meta:
        db_table = 'fnb_expense_categories'


class FnbExpenseHead(FnbNamed):
    category = models.ForeignKey(
        FnbExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heads',
    )

    class Meta:
        db_table = 'fnb_expense_heads'


class FnbExpense(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='fnb_expenses',
        db_index=True,
    )
    head = models.ForeignKey(
        FnbExpenseHead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
    )
    expense_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    revenue_center = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fnb_expenses_created',
    )

    class Meta:
        db_table = 'fnb_expenses'
