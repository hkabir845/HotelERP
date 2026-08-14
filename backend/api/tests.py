"""Smoke tests for hotel GL auto-posting."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.models import (
    AccountsPayable,
    AccountsReceivable,
    ChartOfAccount,
    JournalEntry,
    Tenant,
)
from api.services.hotel_gl import (
    ensure_hotel_accounts,
    post_ap_bill,
    post_ar_invoice,
)


User = get_user_model()


class HotelGlPostingTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Test Hotel', subdomain='testhotel-gl')
        self.user = User.objects.create_user(
            username='gltester',
            email='gl@test.com',
            password='pass12345',
            tenant=self.tenant,
        )
        ensure_hotel_accounts(self.tenant)

    def test_seed_includes_ar_and_cash(self):
        codes = set(
            ChartOfAccount.objects.filter(tenant=self.tenant).values_list('account_code', flat=True)
        )
        self.assertTrue(any(c.endswith('-1130') or c == '1130' for c in codes))
        self.assertTrue(any(c.endswith('-1110') or c == '1110' for c in codes))
        self.assertTrue(any(c.endswith('-2100') or c == '2100' for c in codes))

    def test_ap_bill_posts_balanced_journal(self):
        bill = AccountsPayable.objects.create(
            tenant=self.tenant,
            invoice_number='AP-TEST-1',
            vendor_name='Vendor Co',
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date(),
            amount=Decimal('1500.00'),
            paid_amount=0,
            balance=Decimal('1500.00'),
            created_by=self.user,
        )
        entry = post_ap_bill(bill, user=self.user)
        self.assertIsNotNone(entry)
        self.assertTrue(entry.is_posted)
        self.assertEqual(entry.total_debit, entry.total_credit)
        self.assertEqual(entry.total_debit, Decimal('1500.00'))
        again = post_ap_bill(bill, user=self.user)
        self.assertEqual(again.id, entry.id)
        self.assertEqual(JournalEntry.objects.filter(entry_number=f'AUTO-AP-{bill.id}').count(), 1)

    def test_ar_invoice_posts_to_revenue(self):
        inv = AccountsReceivable.objects.create(
            tenant=self.tenant,
            invoice_number='AR-TEST-1',
            customer_name='Guest',
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date(),
            amount=Decimal('800.00'),
            paid_amount=0,
            balance=Decimal('800.00'),
            created_by=self.user,
        )
        entry = post_ar_invoice(inv, user=self.user)
        self.assertTrue(entry.is_posted)
        self.assertEqual(entry.total_debit, Decimal('800.00'))
