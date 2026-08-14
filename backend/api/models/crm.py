"""CRM customers, leads, quotations, invoices, tasks, and feedback."""
from django.db import models


class CrmLeadSource(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_lead_sources', db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_lead_sources'
        ordering = ['name']


class CrmCustomer(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_customers', db_index=True)
    kind = models.CharField(max_length=20, default='individual', db_index=True)
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True, default='')
    contact_person = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    address = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_customers'
        ordering = ['name']


class CrmLead(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_leads', db_index=True)
    number = models.CharField(max_length=40, db_index=True)
    source = models.ForeignKey(
        CrmLeadSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads'
    )
    customer = models.ForeignKey(
        CrmCustomer, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads'
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')
    expected_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    next_followup = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='new', db_index=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_leads'
        ordering = ['-id']


class CrmQuotation(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_quotations', db_index=True)
    number = models.CharField(max_length=40, db_index=True)
    customer = models.ForeignKey(
        CrmCustomer, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations'
    )
    lead = models.ForeignKey(CrmLead, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')
    valid_until = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='draft', db_index=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_quotations'
        ordering = ['-id']


class CrmInvoice(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_invoices', db_index=True)
    number = models.CharField(max_length=40, db_index=True)
    customer = models.ForeignKey(
        CrmCustomer, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices'
    )
    quotation = models.ForeignKey(
        CrmQuotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices'
    )
    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, default='')
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='unpaid', db_index=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_invoices'
        ordering = ['-id']


class CrmInvoicePayment(models.Model):
    invoice = models.ForeignKey(CrmInvoice, on_delete=models.CASCADE, related_name='payments')
    pay_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, default='cash')
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_invoice_payments'
        ordering = ['-id']


class CrmTask(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_tasks', db_index=True)
    title = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    due_at = models.DateTimeField(null=True, blank=True)
    is_followup = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='open', db_index=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_tasks'
        ordering = ['due_at', '-id']


class CrmFeedback(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_feedback', db_index=True)
    guest_name = models.CharField(max_length=200)
    place = models.CharField(max_length=200, blank=True, default='')
    rating = models.PositiveSmallIntegerField(default=5)
    comments = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, default='open', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_feedback'
        ordering = ['-id']


class CrmComment(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='crm_comments', db_index=True)
    related_kind = models.CharField(max_length=40, default='lead')
    related_name = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField()
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_comments'
        ordering = ['-id']
