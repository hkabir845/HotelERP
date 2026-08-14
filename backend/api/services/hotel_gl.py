"""
Hotel ops → general ledger posting (FSERP-style auto journals).

Keeps classic voucher UX for manual books while auto-posting:
  - AP bills / AP payments
  - AR invoices / AR payments
  - Folio charges & folio payments
  - F&B order completion
  - Inventory purchases & supplier payments
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from api.models import (
    AccountTransaction,
    AccountsPayable,
    AccountsReceivable,
    APPayment,
    ARPayment,
    Budget,
    ChartOfAccount,
    Order,
    PartyType,
    UserAccountPermission,
)
from api.services.hotel_coa import HotelCoaCode, ensure_hotel_coa, resolve_account
from api.services.loan_gl import create_posted_entry
from api.services.party_ledger import get_or_create_party, post_party_entry

TWOPLACES = Decimal('0.01')


def _q(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(TWOPLACES, ROUND_HALF_UP)


def _mirror_party(
    tenant,
    party_type,
    name,
    entry_date,
    *,
    party_id=None,
    debit=0,
    credit=0,
    narration='',
    journal_entry=None,
    related_type=None,
    related_id=None,
    control_code=None,
    loan_payable=False,
):
    """Best-effort party subledger mirror — never fail the GL post."""
    if not name and not party_id:
        return
    try:
        party = get_or_create_party(
            tenant,
            party_type,
            name or 'Party',
            party_id=party_id,
            control_code=control_code,
            loan_payable=loan_payable,
        )
        post_party_entry(
            party,
            entry_date,
            debit=debit,
            credit=credit,
            narration=narration,
            journal_entry=journal_entry,
            related_type=related_type,
            related_id=related_id,
        )
    except Exception:
        # Subledger is secondary to GL; log silently in production paths
        pass


def ensure_hotel_accounts(tenant):
    """Ensure full built-in hotel chart exists."""
    return ensure_hotel_coa(tenant)


def account_by_code(tenant, suffix: str):
    return resolve_account(tenant, suffix)


def book_account(tenant, book: str):
    ensure_hotel_coa(tenant)
    return (
        ChartOfAccount.objects.filter(tenant=tenant, book=book, is_group=False, is_active=True)
        .order_by('id')
        .first()
    )


def settlement_account(tenant, method: str | None):
    """Map cash/card/bank payment methods to Cash or Bank COA."""
    method = (method or 'cash').strip().lower()
    if method in ('card', 'bank', 'bank_transfer', 'cheque', 'check', 'online', 'bkash', 'nagad'):
        return book_account(tenant, 'bank') or account_by_code(tenant, HotelCoaCode.BANK)
    return book_account(tenant, 'cash') or account_by_code(tenant, HotelCoaCode.CASH)


def revenue_code_for_item_type(item_type: str | None) -> str:
    t = (item_type or '').strip().lower()
    if t in ('fnb', 'food', 'beverage', 'f&b', 'restaurant', 'pos'):
        return HotelCoaCode.FNB_REV
    if t in ('banquet', 'event'):
        return HotelCoaCode.BANQUET_REV
    if t in ('spa', 'service', 'laundry'):
        return HotelCoaCode.OTHER_SERVICE_REV
    if t in ('extra', 'other', 'misc'):
        return HotelCoaCode.OTHER_INCOME
    return HotelCoaCode.ROOM_REV


def check_account_permission(user, flag: str):
    """
    Return an error message if denied, else None.

    Default-deny when no UserAccountPermission row: fall back to RBAC capabilities
    so housekeeping/frontdesk cannot post vouchers by calling the API directly.
    Explicit rows still enforce SoD (e.g. purchase_officer cannot post).
    """
    if not user or getattr(user, 'is_superuser', False):
        return None
    role = (getattr(user, 'role', None) or '').lower()
    if role in ('admin', 'superadmin'):
        return None

    from api.rbac import has_capability, CAP_POST_VOUCHERS, CAP_MANAGE_COA, CAP_VIEW_FINANCE

    flag_to_cap = {
        'can_post_vouchers': CAP_POST_VOUCHERS,
        'can_manage_coa': CAP_MANAGE_COA,
        'can_view_reports': CAP_VIEW_FINANCE,
    }

    tenant = getattr(user, 'tenant', None)
    if not tenant and getattr(user, 'tenant_id', None):
        from api.models import Tenant
        tenant = Tenant.objects.filter(id=user.tenant_id).first()

    perm = None
    if tenant:
        perm = UserAccountPermission.objects.filter(tenant=tenant, user=user).first()

    labels = {
        'can_post_vouchers': 'post vouchers',
        'can_view_reports': 'view accounting reports',
        'can_manage_coa': 'manage chart of accounts',
    }

    if perm is not None:
        if not getattr(perm, flag, False):
            return f'You do not have permission to {labels.get(flag, flag)}'
        return None

    cap = flag_to_cap.get(flag)
    if cap and has_capability(role, cap):
        return None
    return f'You do not have permission to {labels.get(flag, flag)}'

def _post(
    tenant,
    entry_number,
    entry_date,
    description,
    lines,
    user=None,
    voucher_type='journal',
    related_type=None,
    related_id=None,
):
    return create_posted_entry(
        tenant=tenant,
        entry_date=entry_date or timezone.now().date(),
        entry_number=entry_number,
        description=description,
        lines=lines,
        user=user,
        voucher_type=voucher_type,
        related_type=related_type,
        related_id=related_id,
    )


def post_ap_bill(bill: AccountsPayable, user=None):
    amount = _q(bill.amount)
    if amount <= 0:
        return None
    tenant = bill.tenant
    expense = bill.expense_account if bill.expense_account_id else account_by_code(tenant, HotelCoaCode.PURCHASES)
    ap = account_by_code(tenant, HotelCoaCode.AP)
    if not expense or not ap:
        raise ValueError('AP or expense account missing — open Chart of Accounts once to seed defaults')
    entry = _post(
        tenant,
        f'AUTO-AP-{bill.id}',
        bill.invoice_date,
        f'AP bill {bill.invoice_number} — {bill.vendor_name}',
        [
            (expense, amount, 0, bill.notes or bill.vendor_name),
            (ap, 0, amount, bill.invoice_number),
        ],
        user=user,
        related_type='ap_bill',
        related_id=bill.id,
    )
    _mirror_party(
        tenant, PartyType.VENDOR, bill.vendor_name, bill.invoice_date,
        party_id=bill.vendor_id, credit=amount,
        narration=f'AP bill {bill.invoice_number}',
        journal_entry=entry, related_type='ap_bill', related_id=bill.id,
    )
    return entry


def post_ap_payment(payment: APPayment, user=None, settlement=None):
    amount = _q(payment.amount)
    if amount <= 0:
        return None
    bill = payment.accounts_payable
    tenant = bill.tenant
    ap = account_by_code(tenant, HotelCoaCode.AP)
    settle = settlement or settlement_account(tenant, payment.payment_method)
    if not ap or not settle:
        raise ValueError('AP or settlement account missing')
    entry = _post(
        tenant,
        f'AUTO-APPAY-{payment.id}',
        payment.payment_date,
        f'AP payment {bill.invoice_number} — {bill.vendor_name}',
        [
            (ap, amount, 0, payment.reference or bill.invoice_number),
            (settle, 0, amount, payment.payment_method or 'cash'),
        ],
        user=user,
        voucher_type='bank_payment' if settle.book == 'bank' else 'cash_payment',
        related_type='ap_payment',
        related_id=payment.id,
    )
    _mirror_party(
        tenant, PartyType.VENDOR, bill.vendor_name, payment.payment_date,
        party_id=bill.vendor_id, debit=amount,
        narration=f'AP payment {bill.invoice_number}',
        journal_entry=entry, related_type='ap_payment', related_id=payment.id,
    )
    return entry


def post_ar_invoice(inv: AccountsReceivable, user=None):
    amount = _q(inv.amount)
    if amount <= 0:
        return None
    tenant = inv.tenant
    ar = account_by_code(tenant, HotelCoaCode.AR)
    revenue = inv.revenue_account if getattr(inv, 'revenue_account_id', None) else account_by_code(tenant, HotelCoaCode.ROOM_REV)
    if not ar or not revenue:
        raise ValueError('AR or revenue account missing')
    entry = _post(
        tenant,
        f'AUTO-AR-{inv.id}',
        inv.invoice_date,
        f'AR invoice {inv.invoice_number} — {inv.customer_name}',
        [
            (ar, amount, 0, inv.notes or inv.customer_name),
            (revenue, 0, amount, inv.invoice_number),
        ],
        user=user,
        related_type='ar_invoice',
        related_id=inv.id,
    )
    ptype = PartyType.CUSTOMER
    if (inv.related_type or '') == 'guest':
        ptype = PartyType.GUEST
    elif (inv.related_type or '') == 'company':
        ptype = PartyType.COMPANY
    _mirror_party(
        tenant, ptype, inv.customer_name, inv.invoice_date,
        party_id=inv.customer_id, debit=amount,
        narration=f'AR invoice {inv.invoice_number}',
        journal_entry=entry, related_type='ar_invoice', related_id=inv.id,
        control_code=HotelCoaCode.AR_CORPORATE if ptype != PartyType.GUEST else HotelCoaCode.AR,
    )
    return entry


def post_ar_payment(payment: ARPayment, user=None, settlement=None):
    amount = _q(payment.amount)
    if amount <= 0:
        return None
    inv = payment.accounts_receivable
    tenant = inv.tenant
    ar = account_by_code(tenant, HotelCoaCode.AR)
    settle = settlement or settlement_account(tenant, payment.payment_method)
    if not ar or not settle:
        raise ValueError('AR or settlement account missing')
    entry = _post(
        tenant,
        f'AUTO-ARPAY-{payment.id}',
        payment.payment_date,
        f'AR receipt {inv.invoice_number} — {inv.customer_name}',
        [
            (settle, amount, 0, payment.payment_method or 'cash'),
            (ar, 0, amount, payment.reference or inv.invoice_number),
        ],
        user=user,
        voucher_type='bank_receipt' if settle.book == 'bank' else 'cash_receipt',
        related_type='ar_payment',
        related_id=payment.id,
    )
    ptype = PartyType.CUSTOMER
    if (inv.related_type or '') == 'guest':
        ptype = PartyType.GUEST
    _mirror_party(
        tenant, ptype, inv.customer_name, payment.payment_date,
        party_id=inv.customer_id, credit=amount,
        narration=f'AR receipt {inv.invoice_number}',
        journal_entry=entry, related_type='ar_payment', related_id=payment.id,
    )
    return entry


def post_folio_charge(tenant, bill_item, user=None, reservation_number: str = ''):
    amount = _q(bill_item.line_total)
    if amount <= 0:
        return None
    ar = account_by_code(tenant, HotelCoaCode.AR)
    revenue = account_by_code(tenant, revenue_code_for_item_type(bill_item.item_type))
    if not ar or not revenue:
        raise ValueError('AR or revenue account missing')
    label = reservation_number or (bill_item.bill.bill_number if bill_item.bill_id else '')
    entry = _post(
        tenant,
        f'AUTO-FOLIO-CHG-{bill_item.id}',
        (bill_item.charge_date.date() if bill_item.charge_date else timezone.now().date()),
        f'Folio charge {label}: {bill_item.description or "charge"}',
        [
            (ar, amount, 0, bill_item.description or 'folio charge'),
            (revenue, 0, amount, bill_item.item_type or 'room_charge'),
        ],
        user=user,
        related_type='folio_charge',
        related_id=bill_item.id,
    )
    guest = getattr(getattr(bill_item, 'bill', None), 'guest', None)
    gname = ''
    gid = None
    if guest:
        gid = guest.id
        gname = getattr(guest, 'full_name', None) or f'{getattr(guest, "first_name", "")} {getattr(guest, "last_name", "")}'.strip()
    if not gname:
        gname = label or f'Folio {getattr(getattr(bill_item, "bill", None), "bill_number", bill_item.id)}'
    _mirror_party(
        tenant, PartyType.GUEST, gname, entry.entry_date if entry else timezone.now().date(),
        party_id=gid, debit=amount,
        narration=f'Folio charge {label}',
        journal_entry=entry, related_type='folio_charge', related_id=bill_item.id,
        control_code=HotelCoaCode.AR,
    )
    return entry


def post_folio_payment(tenant, bill_payment, user=None, reservation_number: str = '', settlement=None):
    amount = _q(bill_payment.amount)
    if amount <= 0:
        return None
    ar = account_by_code(tenant, HotelCoaCode.AR)
    settle = settlement or settlement_account(tenant, bill_payment.payment_method)
    if not ar or not settle:
        raise ValueError('AR or settlement account missing')
    label = reservation_number or (bill_payment.bill.bill_number if bill_payment.bill_id else '')
    pay_date = bill_payment.payment_date
    if hasattr(pay_date, 'date'):
        pay_date = pay_date.date()
    entry = _post(
        tenant,
        f'AUTO-FOLIO-PAY-{bill_payment.id}',
        pay_date or timezone.now().date(),
        f'Folio payment {label}',
        [
            (settle, amount, 0, bill_payment.payment_method or 'cash'),
            (ar, 0, amount, bill_payment.notes or label),
        ],
        user=user,
        voucher_type='bank_receipt' if settle.book == 'bank' else 'cash_receipt',
        related_type='folio_payment',
        related_id=bill_payment.id,
    )
    guest = getattr(getattr(bill_payment, 'bill', None), 'guest', None)
    gname = ''
    gid = None
    if guest:
        gid = guest.id
        gname = getattr(guest, 'full_name', None) or f'{getattr(guest, "first_name", "")} {getattr(guest, "last_name", "")}'.strip()
    if not gname:
        gname = label or 'Guest'
    _mirror_party(
        tenant, PartyType.GUEST, gname, pay_date or timezone.now().date(),
        party_id=gid, credit=amount,
        narration=f'Folio payment {label}',
        journal_entry=entry, related_type='folio_payment', related_id=bill_payment.id,
        control_code=HotelCoaCode.AR,
    )
    return entry


def post_fnb_sale(order: Order, user=None):
    amount = _q(order.total_amount)
    if amount <= 0:
        return None
    tenant = order.tenant
    revenue = account_by_code(tenant, HotelCoaCode.FNB_REV)
    method = (order.payment_method or '').strip().lower()
    unpaid = (order.payment_status or '').lower() in ('pending', 'unpaid', '') and not method
    debit_acc = account_by_code(tenant, HotelCoaCode.AR) if unpaid else settlement_account(tenant, method or 'cash')
    if not revenue or not debit_acc:
        raise ValueError('F&B revenue or settlement account missing')
    entry = _post(
        tenant,
        f'AUTO-FNB-{order.id}',
        (order.completed_at.date() if order.completed_at else timezone.now().date()),
        f'F&B order {order.order_number}',
        [
            (debit_acc, amount, 0, order.payment_method or order.payment_status or 'sale'),
            (revenue, 0, amount, order.order_number),
        ],
        user=user,
        voucher_type='journal' if unpaid else (
            'bank_receipt' if debit_acc.book == 'bank' else 'cash_receipt'
        ),
        related_type='fnb_order',
        related_id=order.id,
    )
    if unpaid:
        pos = getattr(order, 'pos_customer', None)
        if pos:
            _mirror_party(
                tenant, PartyType.CUSTOMER, getattr(pos, 'name', None) or order.guest_name or 'POS customer',
                entry.entry_date if entry else timezone.now().date(),
                party_id=pos.id, debit=amount,
                narration=f'F&B order {order.order_number}',
                journal_entry=entry, related_type='fnb_order', related_id=order.id,
                control_code=HotelCoaCode.AR_CORPORATE,
            )
        elif order.guest_name:
            _mirror_party(
                tenant, PartyType.GUEST, order.guest_name,
                entry.entry_date if entry else timezone.now().date(),
                debit=amount,
                narration=f'F&B order {order.order_number}',
                journal_entry=entry, related_type='fnb_order', related_id=order.id,
                control_code=HotelCoaCode.AR,
            )
    return entry


def post_inventory_purchase(purchase, user=None, expense=None, ap=None):
    amount = _q(purchase.total_amount)
    if amount <= 0:
        return None
    tenant = purchase.tenant
    expense = expense or account_by_code(tenant, HotelCoaCode.PURCHASES)
    ap = ap or account_by_code(tenant, HotelCoaCode.AP)
    if not expense or not ap:
        raise ValueError('Purchase or AP account missing')
    if purchase.is_return:
        lines = [
            (ap, amount, 0, purchase.purchase_number),
            (expense, 0, amount, 'purchase return'),
        ]
    else:
        lines = [
            (expense, amount, 0, purchase.purchase_number),
            (ap, 0, amount, getattr(purchase.supplier, 'name', '') or 'supplier'),
        ]
    entry = _post(
        tenant,
        f'AUTO-PUR-{purchase.id}',
        purchase.purchase_date,
        f'Inventory {"return" if purchase.is_return else "purchase"} {purchase.purchase_number}',
        lines,
        user=user,
        related_type='purchase',
        related_id=purchase.id,
    )
    supplier = getattr(purchase, 'supplier', None)
    sname = getattr(supplier, 'name', None) or 'Supplier'
    sid = getattr(supplier, 'id', None)
    if purchase.is_return:
        _mirror_party(
            tenant, PartyType.SUPPLIER, sname, purchase.purchase_date,
            party_id=sid, debit=amount,
            narration=f'Purchase return {purchase.purchase_number}',
            journal_entry=entry, related_type='purchase', related_id=purchase.id,
        )
    else:
        _mirror_party(
            tenant, PartyType.SUPPLIER, sname, purchase.purchase_date,
            party_id=sid, credit=amount,
            narration=f'Purchase {purchase.purchase_number}',
            journal_entry=entry, related_type='purchase', related_id=purchase.id,
        )
    return entry


def post_supplier_payment(payment, user=None, settlement=None):
    amount = _q(payment.amount)
    if amount <= 0:
        return None
    tenant = payment.tenant
    ap = account_by_code(tenant, HotelCoaCode.AP)
    settle = settlement or settlement_account(tenant, payment.payment_method)
    if not ap or not settle:
        raise ValueError('AP or settlement account missing')
    supplier_name = getattr(getattr(payment, 'supplier', None), 'name', '') or 'supplier'
    entry = _post(
        tenant,
        f'AUTO-SUPPAY-{payment.id}',
        payment.payment_date,
        f'Supplier payment — {supplier_name}',
        [
            (ap, amount, 0, payment.reference or supplier_name),
            (settle, 0, amount, payment.payment_method or 'cash'),
        ],
        user=user,
        voucher_type='bank_payment' if settle.book == 'bank' else 'cash_payment',
        related_type='supplier_payment',
        related_id=payment.id,
    )
    supplier = getattr(payment, 'supplier', None)
    _mirror_party(
        tenant, PartyType.SUPPLIER, supplier_name, payment.payment_date,
        party_id=getattr(supplier, 'id', None), debit=amount,
        narration=f'Supplier payment — {supplier_name}',
        journal_entry=entry, related_type='supplier_payment', related_id=payment.id,
    )
    return entry



    return entry


def _employee_party_name(employee) -> str:
    return (
        getattr(employee, 'full_name', None)
        or f'{getattr(employee, "first_name", "")} {getattr(employee, "last_name", "")}'.strip()
        or employee.employee_number
        or 'Employee'
    )


def post_payroll_accrual(payroll, user=None):
    """
    Approve payroll → books:
      Dr Salaries & Wages (5100) = gross
      Cr Salary Payable (2200) = gross
    Employee party: credit gross (liability).
    Idempotent: AUTO-PAY-ACC-{id}
    """
    if getattr(payroll, 'accrual_journal_id', None):
        return payroll.accrual_journal
    gross = _q(payroll.gross_pay)
    if gross <= 0:
        return None
    tenant = payroll.tenant
    expense = account_by_code(tenant, HotelCoaCode.SALARIES)
    payable = account_by_code(tenant, HotelCoaCode.SALARY_PAYABLE)
    if not expense or not payable:
        raise ValueError('Salary expense (5100) or payable (2200) missing — open Chart of Accounts once')
    entry_date = payroll.pay_period_end or payroll.pay_date or timezone.now().date()
    entry = _post(
        tenant,
        f'AUTO-PAY-ACC-{payroll.id}',
        entry_date,
        f'Payroll accrual {payroll.payroll_number} — {_employee_party_name(payroll.employee)}',
        [
            (expense, gross, 0, payroll.payroll_number),
            (payable, 0, gross, payroll.employee.employee_number),
        ],
        user=user,
        related_type='payroll_accrual',
        related_id=payroll.id,
    )
    _mirror_party(
        tenant,
        PartyType.EMPLOYEE,
        _employee_party_name(payroll.employee),
        entry_date,
        party_id=payroll.employee_id,
        credit=gross,
        narration=f'Payroll accrual {payroll.payroll_number}',
        journal_entry=entry,
        related_type='payroll_accrual',
        related_id=payroll.id,
        control_code=HotelCoaCode.SALARY_PAYABLE,
    )
    payroll.accrual_journal = entry
    payroll.save(update_fields=['accrual_journal', 'updated_at'])
    return entry


def post_payroll_payment(payroll, user=None, settlement=None):
    """
    Pay payroll → books:
      Dr Salary Payable (2200) = net
      Cr Cash/Bank = net
    Employee party: debit net.
    Withheld deductions remain on 2200 / party until remitted.
    Idempotent: AUTO-PAY-PMT-{id}
    """
    if getattr(payroll, 'payment_journal_id', None):
        return payroll.payment_journal
    net = _q(payroll.net_pay)
    if net <= 0:
        return None
    tenant = payroll.tenant
    payable = account_by_code(tenant, HotelCoaCode.SALARY_PAYABLE)
    settle = settlement or settlement_account(tenant, payroll.payment_method)
    if not payable or not settle:
        raise ValueError('Salary payable or settlement account missing')
    entry_date = payroll.pay_date or timezone.now().date()
    entry = _post(
        tenant,
        f'AUTO-PAY-PMT-{payroll.id}',
        entry_date,
        f'Payroll payment {payroll.payroll_number} — {_employee_party_name(payroll.employee)}',
        [
            (payable, net, 0, payroll.payroll_number),
            (settle, 0, net, payroll.payment_method or 'bank'),
        ],
        user=user,
        voucher_type='bank_payment' if settle.book == 'bank' else 'cash_payment',
        related_type='payroll_payment',
        related_id=payroll.id,
    )
    _mirror_party(
        tenant,
        PartyType.EMPLOYEE,
        _employee_party_name(payroll.employee),
        entry_date,
        party_id=payroll.employee_id,
        debit=net,
        narration=f'Payroll payment {payroll.payroll_number}',
        journal_entry=entry,
        related_type='payroll_payment',
        related_id=payroll.id,
        control_code=HotelCoaCode.SALARY_PAYABLE,
    )
    payroll.payment_journal = entry
    payroll.save(update_fields=['payment_journal', 'updated_at'])
    return entry


def reverse_payroll_accrual(payroll, user=None):
    """Undo accrual JE + party lines when cancelling an approved (unpaid) slip."""
    from api.models import PartyLedgerEntry
    from api.services.coa_opening import _undo_posted_entry
    from api.services.party_ledger import control_is_debit_normal

    if payroll.payment_journal_id:
        raise ValueError('Cannot reverse accrual after payment — void payment first')
    if not payroll.accrual_journal_id:
        return None
    # Reverse party lines for this accrual
    for line in PartyLedgerEntry.objects.filter(
        related_type='payroll_accrual', related_id=payroll.id,
    ).select_related('party_account', 'party_account__control_account'):
        party = line.party_account
        debit_normal = control_is_debit_normal(party.control_account)
        delta = (line.debit - line.credit) if debit_normal else (line.credit - line.debit)
        party.current_balance = _q(party.current_balance) - _q(delta)
        party.save(update_fields=['current_balance', 'updated_at'])
        line.delete()
    _undo_posted_entry(payroll.accrual_journal)
    payroll.accrual_journal = None
    payroll.save(update_fields=['accrual_journal', 'updated_at'])
    return payroll


def refresh_budget_actual(budget: Budget) -> Budget:
    account = budget.account
    qs = AccountTransaction.objects.filter(
        account=account,
        journal_entry__is_posted=True,
        transaction_date__gte=budget.period_start,
        transaction_date__lte=budget.period_end,
    )
    debit = qs.filter(transaction_type='debit').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    credit = qs.filter(transaction_type='credit').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    if account.account_type in ('asset', 'expense'):
        actual = debit - credit
    else:
        actual = credit - debit
    actual = _q(actual)
    budget.actual_amount = actual
    budget.variance = _q(budget.budgeted_amount) - actual
    budget.save(update_fields=['actual_amount', 'variance', 'updated_at'])
    return budget


def refresh_tenant_budgets(tenant):
    for row in Budget.objects.filter(tenant=tenant, is_active=True).select_related('account'):
        refresh_budget_actual(row)
