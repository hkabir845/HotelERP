"""Resolve diggable root sources with human descriptions for report drill-down."""
from __future__ import annotations

from api.models import (
    AccountsPayable,
    AccountsReceivable,
    APPayment,
    ARPayment,
    ChartOfAccount,
    Order,
    Payroll,
)


SOURCE_CATALOG = {
    'ap_bill': ('Vendor bill', '/accounts/payable'),
    'ap_payment': ('AP payment', '/accounts/payable/payments'),
    'ar_invoice': ('Customer invoice', '/accounts/receivable'),
    'ar_payment': ('AR receipt', '/accounts/receivable/payments'),
    'folio_charge': ('Folio charge', '/frontdesk/pending-folio'),
    'folio_payment': ('Folio payment', '/frontdesk/pending-folio'),
    'fnb_order': ('F&B order', '/fnb/orders/active'),
    'purchase': ('Inventory purchase', '/inventory/purchases'),
    'supplier_payment': ('Supplier payment', '/inventory/suppliers/payments'),
    'loan_disbursement': ('Loan disbursement', '/accounts/loans'),
    'loan_repayment': ('Loan repayment', '/accounts/loans'),
    'loan_accrual': ('Loan interest accrual', '/accounts/loans'),
    'loan_counterparty': ('Loan counterparty', '/accounts/loans'),
    'coa_opening': ('COA opening balance', '/accounts/chart-of-accounts/accounts'),
    'party_opening': ('Party opening', '/accounts/parties'),
    'payroll_accrual': ('Payroll accrual', '/hr/payroll'),
    'payroll_payment': ('Payroll payment', '/hr/payroll/payments'),
}

ENTRY_SOURCE_PREFIXES = (
    ('AUTO-APPAY-', 'ap_payment'),
    ('AUTO-ARPAY-', 'ar_payment'),
    ('AUTO-FOLIO-CHG-', 'folio_charge'),
    ('AUTO-FOLIO-PAY-', 'folio_payment'),
    ('AUTO-LOAN-CP-OB-', 'loan_counterparty'),
    ('AUTO-LOAN-DISP-', 'loan_disbursement'),
    ('AUTO-LOAN-PMT-REV-', 'loan_repayment'),
    ('AUTO-LOAN-PMT-', 'loan_repayment'),
    ('AUTO-LOAN-ACC-REV-', 'loan_accrual'),
    ('AUTO-LOAN-ACC-', 'loan_accrual'),
    ('AUTO-PAY-ACC-', 'payroll_accrual'),
    ('AUTO-PAY-PMT-', 'payroll_payment'),
    ('AUTO-SUPPAY-', 'supplier_payment'),
    ('AUTO-PUR-', 'purchase'),
    ('AUTO-FNB-', 'fnb_order'),
    ('AUTO-COA-OB-', 'coa_opening'),
    ('AUTO-AP-', 'ap_bill'),
    ('AUTO-AR-', 'ar_invoice'),
)


def infer_related_from_entry_number(entry_number):
    number = (entry_number or '').strip()
    for prefix, related_type in ENTRY_SOURCE_PREFIXES:
        if number.startswith(prefix):
            suffix = number[len(prefix):]
            try:
                return related_type, int(suffix)
            except (TypeError, ValueError):
                return related_type, None
    return None, None


def _money(v) -> str:
    try:
        return f'{float(v):,.2f}'
    except (TypeError, ValueError):
        return str(v or 0)


def _empty():
    return {
        'related_type': None,
        'related_id': None,
        'source_label': None,
        'source_path': None,
        'source_description': None,
        'drill_chain': [],
    }


def _detail_for(tenant, rtype: str, rid: int | None):
    """Return (description, path, parent_chain_steps)."""
    label, base_path = SOURCE_CATALOG.get(rtype, (rtype.replace('_', ' ').title(), None))
    path = base_path
    description = None
    parents = []

    if not rid:
        return description, path, parents

    try:
        if rtype == 'ap_bill':
            row = AccountsPayable.objects.filter(tenant=tenant, id=rid).first()
            if row:
                description = (
                    f'{row.invoice_number} — {row.vendor_name}; '
                    f'amount {_money(row.amount)}, balance {_money(row.balance)}, '
                    f'due {row.due_date}'
                )
                path = '/accounts/payable'
        elif rtype == 'ap_payment':
            row = APPayment.objects.select_related('accounts_payable').filter(id=rid).first()
            if row and row.accounts_payable.tenant_id == tenant.id:
                bill = row.accounts_payable
                description = (
                    f'Payment {_money(row.amount)} on {row.payment_date} '
                    f'({row.payment_method or "cash"}) for bill {bill.invoice_number} — {bill.vendor_name}'
                )
                path = '/accounts/payable/payments'
                parents.append({
                    'step': 'ap_bill',
                    'label': 'Vendor bill',
                    'description': f'{bill.invoice_number} — {bill.vendor_name}; amount {_money(bill.amount)}',
                    'path': '/accounts/payable',
                    'related_id': bill.id,
                })
        elif rtype == 'ar_invoice':
            row = AccountsReceivable.objects.filter(tenant=tenant, id=rid).first()
            if row:
                description = (
                    f'{row.invoice_number} — {row.customer_name}; '
                    f'amount {_money(row.amount)}, balance {_money(row.balance)}, '
                    f'due {row.due_date}'
                )
                path = '/accounts/receivable'
        elif rtype == 'ar_payment':
            row = ARPayment.objects.select_related('accounts_receivable').filter(id=rid).first()
            if row and row.accounts_receivable.tenant_id == tenant.id:
                inv = row.accounts_receivable
                description = (
                    f'Receipt {_money(row.amount)} on {row.payment_date} '
                    f'({row.payment_method or "cash"}) for invoice {inv.invoice_number} — {inv.customer_name}'
                )
                path = '/accounts/receivable/payments'
                parents.append({
                    'step': 'ar_invoice',
                    'label': 'Customer invoice',
                    'description': f'{inv.invoice_number} — {inv.customer_name}; amount {_money(inv.amount)}',
                    'path': '/accounts/receivable',
                    'related_id': inv.id,
                })
        elif rtype in ('folio_charge', 'folio_payment'):
            from api.models.billing import BillItem, BillPayment
            if rtype == 'folio_charge':
                item = BillItem.objects.select_related('bill', 'bill__guest').filter(id=rid).first()
                if item and item.bill and item.bill.tenant_id == tenant.id:
                    bill = item.bill
                    guest = ''
                    if bill.guest_id:
                        guest = getattr(bill.guest, 'full_name', None) or f'{bill.guest.first_name} {bill.guest.last_name}'.strip()
                    description = (
                        f'Bill {bill.bill_number}'
                        + (f' — {guest}' if guest else '')
                        + f'; charge “{item.description or item.item_type or "charge"}” '
                        f'{_money(item.line_total)}'
                    )
                    path = '/frontdesk/pending-folio'
                    parents.append({
                        'step': 'folio_bill',
                        'label': 'Guest folio',
                        'description': f'Bill {bill.bill_number}' + (f' — {guest}' if guest else ''),
                        'path': '/frontdesk/pending-folio',
                        'related_id': bill.id,
                    })
            else:
                pay = BillPayment.objects.select_related('bill', 'bill__guest').filter(id=rid).first()
                if pay and pay.bill and pay.bill.tenant_id == tenant.id:
                    bill = pay.bill
                    guest = ''
                    if bill.guest_id:
                        guest = getattr(bill.guest, 'full_name', None) or f'{bill.guest.first_name} {bill.guest.last_name}'.strip()
                    description = (
                        f'Bill {bill.bill_number}'
                        + (f' — {guest}' if guest else '')
                        + f'; payment {_money(pay.amount)} ({pay.payment_method or "cash"})'
                    )
                    path = '/frontdesk/pending-folio'
                    parents.append({
                        'step': 'folio_bill',
                        'label': 'Guest folio',
                        'description': f'Bill {bill.bill_number}' + (f' — {guest}' if guest else ''),
                        'path': '/frontdesk/pending-folio',
                        'related_id': bill.id,
                    })
        elif rtype == 'fnb_order':
            row = Order.objects.filter(tenant=tenant, id=rid).first()
            if row:
                description = (
                    f'Order {row.order_number}; total {_money(row.total_amount)}; '
                    f'{row.guest_name or "walk-in"}; status {row.status}'
                )
                path = '/fnb/orders/active'
        elif rtype == 'purchase':
            from api.models.inventory import Purchase
            row = Purchase.objects.select_related('supplier').filter(tenant=tenant, id=rid).first()
            if row:
                sname = getattr(row.supplier, 'name', '') or 'supplier'
                description = (
                    f'{row.purchase_number} — {sname}; '
                    f'{"return " if row.is_return else ""}total {_money(row.total_amount)} on {row.purchase_date}'
                )
                path = '/inventory/purchases'
        elif rtype == 'supplier_payment':
            from api.models.inventory import SupplierPayment
            row = SupplierPayment.objects.select_related('supplier').filter(tenant=tenant, id=rid).first()
            if row:
                sname = getattr(row.supplier, 'name', '') or 'supplier'
                description = (
                    f'Payment {_money(row.amount)} to {sname} on {row.payment_date} '
                    f'({row.payment_method or "cash"})'
                )
                path = '/inventory/suppliers/payments'
        elif rtype in ('loan_disbursement', 'loan_repayment', 'loan_accrual', 'loan_counterparty'):
            from api.models import LoanCounterparty, LoanDisbursement, LoanRepayment, LoanInterestAccrual
            if rtype == 'loan_counterparty':
                cp = LoanCounterparty.objects.filter(tenant=tenant, id=rid).first()
                if cp:
                    description = f'{cp.code} — {cp.name}; opening {_money(cp.opening_balance)}'
            elif rtype == 'loan_disbursement':
                row = LoanDisbursement.objects.select_related('loan', 'loan__counterparty').filter(id=rid).first()
                if row and row.loan.tenant_id == tenant.id:
                    description = (
                        f'Disburse {_money(row.amount)} on {row.disbursement_date} '
                        f'for {row.loan.loan_no} ({row.loan.counterparty.name})'
                    )
            elif rtype == 'loan_repayment':
                row = LoanRepayment.objects.select_related('loan', 'loan__counterparty').filter(id=rid).first()
                if row and row.loan.tenant_id == tenant.id:
                    description = (
                        f'Repay {_money(row.amount)} on {row.repayment_date} '
                        f'for {row.loan.loan_no} ({row.loan.counterparty.name})'
                    )
            elif rtype == 'loan_accrual':
                row = LoanInterestAccrual.objects.select_related('loan', 'loan__counterparty').filter(id=rid).first()
                if row and row.loan.tenant_id == tenant.id:
                    description = (
                        f'Interest {_money(row.amount)} on {row.accrual_date} '
                        f'for {row.loan.loan_no}'
                    )
            path = '/accounts/loans'
        elif rtype == 'coa_opening':
            acc = ChartOfAccount.objects.filter(tenant=tenant, id=rid).first()
            if acc:
                description = (
                    f'{acc.account_code} {acc.account_name}; '
                    f'opening {_money(acc.opening_balance)}'
                    + (f' as of {acc.opening_balance_as_of}' if acc.opening_balance_as_of else '')
                )
                path = '/accounts/chart-of-accounts/accounts'
        elif rtype == 'party_opening':
            from api.models import PartyAccount
            party = PartyAccount.objects.filter(tenant=tenant, id=rid).first()
            if party:
                description = f'{party.code} {party.name}; opening {_money(party.opening_balance)}'
                path = f'/accounts/parties/{party.id}'
        elif rtype in ('payroll_accrual', 'payroll_payment'):
            row = Payroll.objects.select_related('employee').filter(tenant=tenant, id=rid).first()
            if row:
                description = (
                    f'{row.payroll_number} — {row.employee.full_name}; '
                    f'gross {_money(row.gross_pay)}, net {_money(row.net_pay)}, '
                    f'period {row.pay_period_start} to {row.pay_period_end}'
                )
                path = '/hr/payroll'
    except Exception:
        pass

    return description, path, parents


def resolve_source(tenant=None, related_type=None, related_id=None, entry_number=None, journal_description=None):
    """Return diggable source metadata including description and optional parent chain."""
    rtype = related_type or None
    rid = related_id
    if not rtype:
        rtype, rid = infer_related_from_entry_number(entry_number)
    if not rtype:
        empty = _empty()
        if journal_description:
            empty['source_description'] = journal_description
        return empty

    label, path = SOURCE_CATALOG.get(rtype, (rtype.replace('_', ' ').title(), None))
    description = None
    parents = []
    if tenant is not None:
        description, path, parents = _detail_for(tenant, rtype, rid)
    if not description and journal_description:
        description = journal_description
    if not description and rid:
        description = f'{label} #{rid}'

    chain = [
        {
            'step': rtype,
            'label': label,
            'description': description,
            'path': path,
            'related_id': rid,
        }
    ] + parents

    return {
        'related_type': rtype,
        'related_id': rid,
        'source_label': label,
        'source_path': path,
        'source_description': description,
        'drill_chain': chain,
    }


def build_voucher_drill_chain(entry, lines=None):
    """Full dig path: journal → root source → parent document(s)."""
    tenant = entry.tenant
    lines = lines if lines is not None else list(entry.transactions.all())
    related_type = None
    related_id = None
    for line in lines:
        if line.related_type:
            related_type = line.related_type
            related_id = line.related_id
            break
    source = resolve_source(
        tenant,
        related_type,
        related_id,
        entry.entry_number,
        journal_description=entry.description,
    )
    chain = [
        {
            'step': 'journal',
            'label': 'Journal voucher',
            'description': (
                f'{entry.entry_number} on {entry.entry_date}: '
                f'{entry.description or entry.voucher_type} · '
                f'debit {_money(entry.total_debit)} / credit {_money(entry.total_credit)}'
            ),
            'path': f'/accounts/vouchers/{entry.id}',
            'related_id': entry.id,
        }
    ]
    for step in source.get('drill_chain') or []:
        if step.get('label'):
            chain.append(step)
    source['drill_chain'] = chain
    return source
