"""
Built-in hotel Chart of Accounts — codes, purposes, and seed rows.

Mirrors FSERP's erp_coa_defaults pattern: resolve by stable account_code suffix,
never by hardcoded primary keys. Frontend `lib/coaDefaults.ts` stays in sync.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.models import ChartOfAccount


@dataclass(frozen=True)
class HotelCoaPurpose:
    key: str
    module: str
    label: str
    account_code: str
    hint: str


class HotelCoaCode:
    """Stable suffixes — keep in sync with frontend/lib/coaDefaults.ts."""

    # Assets / bank & cash
    CASH = '1110'
    PETTY_CASH = '1115'
    BANK = '1120'
    BANK_CARD = '1125'
    AR = '1130'
    AR_CORPORATE = '1135'
    INV_FOOD = '1210'
    INV_BEVERAGE = '1220'
    INV_SUPPLIES = '1230'
    PREPAID_RENT = '1310'
    PREPAID_OTHER = '1320'
    FA_BUILDINGS = '1510'
    FA_EQUIPMENT = '1520'
    FA_VEHICLES = '1530'
    FA_ACCUM_DEPR = '1550'
    LOAN_RECEIVABLE = '1160'
    LOAN_INT_RECV = '1165'

    # Liabilities
    AP = '2100'
    AP_FOOD = '2110'
    GUEST_DEPOSITS = '2120'
    VAT_PAYABLE = '2130'
    SALARY_PAYABLE = '2200'
    ACCRUED_EXP = '2300'
    LOAN_PAYABLE = '2410'
    LOAN_INT_PAY = '2415'

    # Equity
    CAPITAL = '3100'
    OPENING_EQUITY = '3200'
    RETAINED = '3300'

    # Revenue / income
    ROOM_REV = '4100'
    ROOM_PREMIUM = '4110'
    FNB_REV = '4200'
    BANQUET_REV = '4210'
    OTHER_SERVICE_REV = '4220'
    OTHER_INCOME = '4300'
    INTEREST_INCOME = '4410'

    # Expenses / COGS
    SALARIES = '5100'
    UTILITIES = '5200'
    PURCHASES = '5300'
    BEVERAGE_COST = '5310'
    COGS = '5400'
    HK_SUPPLIES = '5500'
    ELECTRIC = '6100'
    WATER = '6110'
    RENT_BUILDING = '6200'
    RENT_EQUIPMENT = '6210'
    REPAIRS = '6300'
    DEPR_EXP = '6320'
    MARKETING = '6400'
    INSURANCE = '6500'
    BANK_FEES = '6600'
    INTEREST_EXPENSE = '6620'
    ADMIN = '6900'
    LAUNDRY = '6910'
    GENERAL_OPEX = '6920'


# (code, name, account_type, is_group, book, parent_code)
HOTEL_COA_ROWS: list[tuple[str, str, str, bool, str, str | None]] = [
    ('1000', 'Assets', 'asset', True, '', None),
    ('1100', 'Current Assets', 'asset', True, '', '1000'),
    ('1110', 'Cash on Hand', 'asset', False, 'cash', '1100'),
    ('1115', 'Petty Cash', 'asset', False, 'cash', '1100'),
    ('1120', 'Bank — Operating', 'asset', False, 'bank', '1100'),
    ('1125', 'Bank — Card Settlement', 'asset', False, 'bank', '1100'),
    ('1130', 'Accounts Receivable — Guests', 'asset', False, 'ar', '1100'),
    ('1135', 'Accounts Receivable — Corporate / Agents', 'asset', False, 'ar', '1100'),
    ('1150', 'Loans & Advances', 'asset', True, '', '1100'),
    ('1160', 'Loans Receivable — Principal', 'asset', False, 'loan_recv', '1150'),
    ('1165', 'Accrued Interest Receivable', 'asset', False, 'loan_acc_a', '1150'),
    ('1200', 'Inventory', 'asset', True, '', '1000'),
    ('1210', 'Food Inventory', 'asset', False, '', '1200'),
    ('1220', 'Beverage Inventory', 'asset', False, '', '1200'),
    ('1230', 'Amenities & Supplies Inventory', 'asset', False, '', '1200'),
    ('1300', 'Prepaid Expenses', 'asset', True, '', '1000'),
    ('1310', 'Prepaid Rent / Lease', 'asset', False, '', '1300'),
    ('1320', 'Prepaid Other', 'asset', False, '', '1300'),
    ('1500', 'Fixed Assets', 'asset', True, '', '1000'),
    ('1510', 'Buildings & Leasehold', 'asset', False, '', '1500'),
    ('1520', 'Furniture & Equipment', 'asset', False, '', '1500'),
    ('1530', 'Vehicles', 'asset', False, '', '1500'),
    ('1550', 'Accumulated Depreciation', 'asset', False, '', '1500'),
    ('2000', 'Liabilities', 'liability', True, '', None),
    ('2100', 'Accounts Payable — Trade', 'liability', False, '', '2000'),
    ('2110', 'Accounts Payable — Food & Beverage', 'liability', False, '', '2000'),
    ('2120', 'Guest Advance Deposits', 'liability', False, '', '2000'),
    ('2130', 'VAT / Tax Payable', 'liability', False, '', '2000'),
    ('2200', 'Salary Payable', 'liability', False, '', '2000'),
    ('2300', 'Accrued Expenses', 'liability', False, '', '2000'),
    ('2400', 'Loans Payable', 'liability', True, '', '2000'),
    ('2410', 'Loans Payable — Principal', 'liability', False, 'loan_pay', '2400'),
    ('2415', 'Accrued Interest Payable', 'liability', False, 'loan_acc_l', '2400'),
    ('3000', 'Equity', 'equity', True, '', None),
    ('3100', 'Owner Capital', 'equity', False, '', '3000'),
    ('3200', 'Opening Balance Equity', 'equity', False, 'obe', '3000'),
    ('3300', 'Retained Earnings', 'equity', False, '', '3000'),
    ('4000', 'Revenue', 'revenue', True, '', None),
    ('4100', 'Room Revenue', 'revenue', False, '', '4000'),
    ('4110', 'Room Revenue — Premium / Suite', 'revenue', False, '', '4000'),
    ('4200', 'F&B Revenue', 'revenue', False, '', '4000'),
    ('4210', 'Banquet / Event Revenue', 'revenue', False, '', '4000'),
    ('4220', 'Spa & Other Services', 'revenue', False, '', '4000'),
    ('4300', 'Other Income', 'revenue', False, '', '4000'),
    ('4410', 'Interest Income — Loans', 'revenue', False, 'loan_int_in', '4000'),
    ('5000', 'Expenses', 'expense', True, '', None),
    ('5100', 'Salaries & Wages', 'expense', False, '', '5000'),
    ('5200', 'Utilities (General)', 'expense', False, '', '5000'),
    ('5300', 'Purchases / Food Cost', 'expense', False, '', '5000'),
    ('5310', 'Beverage Cost', 'expense', False, '', '5000'),
    ('5400', 'Cost of Goods Sold', 'expense', False, '', '5000'),
    ('5500', 'Housekeeping Supplies', 'expense', False, '', '5000'),
    ('6100', 'Electricity', 'expense', False, '', '5000'),
    ('6110', 'Water & Sewer', 'expense', False, '', '5000'),
    ('6200', 'Rent / Lease — Building', 'expense', False, '', '5000'),
    ('6210', 'Lease — Equipment & Vehicles', 'expense', False, '', '5000'),
    ('6300', 'Repairs & Maintenance', 'expense', False, '', '5000'),
    ('6320', 'Depreciation Expense', 'expense', False, '', '5000'),
    ('6400', 'Marketing & Sales', 'expense', False, '', '5000'),
    ('6500', 'Insurance', 'expense', False, '', '5000'),
    ('6600', 'Bank Charges', 'expense', False, '', '5000'),
    ('6620', 'Interest Expense — Loans', 'expense', False, 'loan_int_ex', '5000'),
    ('6900', 'Office & Administration', 'expense', False, '', '5000'),
    ('6910', 'Laundry & Outsourced Services', 'expense', False, '', '5000'),
    ('6920', 'General Operating Expenses', 'expense', False, '', '5000'),
]


HOTEL_COA_PURPOSES: tuple[HotelCoaPurpose, ...] = (
    HotelCoaPurpose('bank.cash', 'bank', 'Cash on hand', HotelCoaCode.CASH, 'Folio cash receipts, petty cash, cash vouchers.'),
    HotelCoaPurpose('bank.petty', 'bank', 'Petty cash', HotelCoaCode.PETTY_CASH, 'Small cash expenses.'),
    HotelCoaPurpose('bank.operating', 'bank', 'Operating bank', HotelCoaCode.BANK, 'Default bank settlement for payments and receipts.'),
    HotelCoaPurpose('bank.card', 'bank', 'Card settlement bank', HotelCoaCode.BANK_CARD, 'Card / POS settlements.'),
    HotelCoaPurpose('ar.guests', 'receivable', 'Guest receivables', HotelCoaCode.AR, 'Folio charges and city-ledger AR.'),
    HotelCoaPurpose('ar.corporate', 'receivable', 'Corporate / agent AR', HotelCoaCode.AR_CORPORATE, 'Company and travel-agent invoices.'),
    HotelCoaPurpose('ap.trade', 'payable', 'Trade payables', HotelCoaCode.AP, 'Vendor bills and supplier AP.'),
    HotelCoaPurpose('ap.food', 'payable', 'F&B payables', HotelCoaCode.AP_FOOD, 'Food and beverage supplier bills.'),
    HotelCoaPurpose('liability.guest_deposits', 'payable', 'Guest advance deposits', HotelCoaCode.GUEST_DEPOSITS, 'Advance deposits before stay.'),
    HotelCoaPurpose('liability.vat', 'payable', 'VAT payable', HotelCoaCode.VAT_PAYABLE, 'Output tax liability.'),
    HotelCoaPurpose('income.room', 'income', 'Room revenue', HotelCoaCode.ROOM_REV, 'Default room / folio room charges.'),
    HotelCoaPurpose('income.room_premium', 'income', 'Premium room revenue', HotelCoaCode.ROOM_PREMIUM, 'Suite / premium room rates.'),
    HotelCoaPurpose('income.fnb', 'income', 'F&B revenue', HotelCoaCode.FNB_REV, 'Restaurant and room-service sales.'),
    HotelCoaPurpose('income.banquet', 'income', 'Banquet revenue', HotelCoaCode.BANQUET_REV, 'Events and banquet folio.'),
    HotelCoaPurpose('income.other_service', 'income', 'Other service revenue', HotelCoaCode.OTHER_SERVICE_REV, 'Spa, laundry guest charges, extras.'),
    HotelCoaPurpose('income.other', 'income', 'Other income', HotelCoaCode.OTHER_INCOME, 'Miscellaneous income.'),
    HotelCoaPurpose('income.interest_loan', 'loan', 'Interest income (loans)', HotelCoaCode.INTEREST_INCOME, 'Interest on loans receivable.'),
    HotelCoaPurpose('expense.purchases', 'expense', 'Purchases / food cost', HotelCoaCode.PURCHASES, 'Default AP bill and inventory purchase expense.'),
    HotelCoaPurpose('expense.beverage', 'expense', 'Beverage cost', HotelCoaCode.BEVERAGE_COST, 'Beverage purchases.'),
    HotelCoaPurpose('expense.cogs', 'expense', 'Cost of goods sold', HotelCoaCode.COGS, 'COGS recognition.'),
    HotelCoaPurpose('expense.salaries', 'expense', 'Salaries & wages', HotelCoaCode.SALARIES, 'Payroll expense.'),
    HotelCoaPurpose('expense.utilities', 'expense', 'Utilities', HotelCoaCode.UTILITIES, 'General utility bills.'),
    HotelCoaPurpose('expense.electric', 'expense', 'Electricity', HotelCoaCode.ELECTRIC, 'Electric utility bills.'),
    HotelCoaPurpose('expense.water', 'expense', 'Water', HotelCoaCode.WATER, 'Water utility bills.'),
    HotelCoaPurpose('expense.rent', 'expense', 'Rent / lease — building', HotelCoaCode.RENT_BUILDING, 'Property rental expense.'),
    HotelCoaPurpose('expense.rent_equipment', 'expense', 'Equipment lease', HotelCoaCode.RENT_EQUIPMENT, 'Equipment / vehicle leases.'),
    HotelCoaPurpose('expense.repairs', 'expense', 'Repairs & maintenance', HotelCoaCode.REPAIRS, 'Maintenance bills.'),
    HotelCoaPurpose('expense.hk_supplies', 'expense', 'Housekeeping supplies', HotelCoaCode.HK_SUPPLIES, 'HK amenity and supply costs.'),
    HotelCoaPurpose('expense.marketing', 'expense', 'Marketing', HotelCoaCode.MARKETING, 'Advertising and sales expense.'),
    HotelCoaPurpose('expense.insurance', 'expense', 'Insurance', HotelCoaCode.INSURANCE, 'Insurance premiums.'),
    HotelCoaPurpose('expense.bank_fees', 'expense', 'Bank charges', HotelCoaCode.BANK_FEES, 'Bank fees and charges.'),
    HotelCoaPurpose('expense.admin', 'expense', 'Office & admin', HotelCoaCode.ADMIN, 'General administration.'),
    HotelCoaPurpose('expense.laundry', 'expense', 'Laundry / outsourced', HotelCoaCode.LAUNDRY, 'Outsourced laundry services.'),
    HotelCoaPurpose('expense.general', 'expense', 'General operating', HotelCoaCode.GENERAL_OPEX, 'Fallback operating expense.'),
    HotelCoaPurpose('expense.interest_loan', 'loan', 'Interest expense (loans)', HotelCoaCode.INTEREST_EXPENSE, 'Interest on borrowings.'),
    HotelCoaPurpose('loan.principal_recv', 'loan', 'Loans receivable', HotelCoaCode.LOAN_RECEIVABLE, 'Principal for loans lent.'),
    HotelCoaPurpose('loan.principal_pay', 'loan', 'Loans payable', HotelCoaCode.LOAN_PAYABLE, 'Principal for loans borrowed.'),
    HotelCoaPurpose('loan.accrual_recv', 'loan', 'Accrued interest receivable', HotelCoaCode.LOAN_INT_RECV, 'Interest accrual asset.'),
    HotelCoaPurpose('loan.accrual_pay', 'loan', 'Accrued interest payable', HotelCoaCode.LOAN_INT_PAY, 'Interest accrual liability.'),
    HotelCoaPurpose('budget.expense', 'budget', 'Default budget expense', HotelCoaCode.GENERAL_OPEX, 'Suggested account when creating expense budgets.'),
    HotelCoaPurpose('budget.revenue', 'budget', 'Default budget revenue', HotelCoaCode.ROOM_REV, 'Suggested account when creating revenue budgets.'),
    HotelCoaPurpose('voucher.payment_expense', 'voucher', 'Payment voucher expense', HotelCoaCode.GENERAL_OPEX, 'Suggested debit on cash/bank payment vouchers.'),
    HotelCoaPurpose('voucher.receipt_income', 'voucher', 'Receipt voucher income', HotelCoaCode.OTHER_INCOME, 'Suggested credit on cash/bank receipt vouchers.'),
)


SETTLEMENT_PREFERENCE = (HotelCoaCode.BANK, HotelCoaCode.CASH)


def _suffix(code: str) -> str:
    """Normalize to plain template code (supports legacy '1-1110' and plain '1110')."""
    code = (code or '').strip()
    if '-' in code:
        left, right = code.split('-', 1)
        if left.isdigit() and right:
            return right
    return code


def chart_by_suffix(tenant) -> dict[str, ChartOfAccount]:
    by: dict[str, ChartOfAccount] = {}
    for acc in ChartOfAccount.objects.filter(tenant=tenant):
        by[_suffix(acc.account_code)] = acc
    return by


def _normalize_existing_codes(tenant) -> None:
    """One-shot normalize legacy tenant-prefixed codes for this tenant."""
    for row in ChartOfAccount.objects.filter(tenant=tenant):
        code = (row.account_code or '').strip()
        plain = _suffix(code)
        if plain == code:
            continue
        if ChartOfAccount.objects.filter(tenant=tenant, account_code=plain).exclude(pk=row.pk).exists():
            continue
        row.account_code = plain
        row.save(update_fields=['account_code', 'updated_at'])


def ensure_hotel_coa(tenant) -> dict[str, ChartOfAccount]:
    """Idempotently seed the full built-in hotel chart for a tenant."""
    _normalize_existing_codes(tenant)
    by = chart_by_suffix(tenant)
    for code, name, acc_type, is_group, book, parent_code in HOTEL_COA_ROWS:
        if code in by:
            # Keep books / system flags healthy on upgrades; normalize display code
            row = by[code]
            changed = []
            if row.account_code != code:
                if not ChartOfAccount.objects.filter(tenant=tenant, account_code=code).exclude(pk=row.pk).exists():
                    row.account_code = code
                    changed.append('account_code')
            if book and row.book != book:
                row.book = book
                changed.append('book')
            if not row.is_system_account:
                row.is_system_account = True
                changed.append('is_system_account')
            if changed:
                row.save(update_fields=changed + ['updated_at'])
            continue
        parent = by.get(parent_code) if parent_code else None
        if parent_code and not parent:
            parent = None
        by[code] = ChartOfAccount.objects.create(
            tenant=tenant,
            account_code=code,  # FSERP-style plain code (unique per tenant)
            account_name=name,
            account_type=acc_type,
            parent_account=parent,
            is_group=is_group,
            book=book,
            is_system_account=True,
            is_active=True,
        )
    # Second pass: attach missing parents
    by = chart_by_suffix(tenant)
    for code, name, acc_type, is_group, book, parent_code in HOTEL_COA_ROWS:
        row = by.get(code)
        if not row or not parent_code:
            continue
        parent = by.get(parent_code)
        if parent and row.parent_account_id != parent.id:
            row.parent_account = parent
            row.save(update_fields=['parent_account', 'updated_at'])
    return by


def resolve_account(tenant, code: str):
    ensure_hotel_coa(tenant)
    code = _suffix(code)
    return (
        ChartOfAccount.objects.filter(tenant=tenant, account_code=code, is_active=True)
        .order_by('id')
        .first()
        or ChartOfAccount.objects.filter(tenant=tenant, account_code__endswith=f'-{code}', is_active=True)
        .order_by('id')
        .first()
    )


def purpose_code(key: str) -> str | None:
    for p in HOTEL_COA_PURPOSES:
        if p.key == key:
            return p.account_code
    return None


def erp_defaults_payload(tenant) -> dict[str, Any]:
    """Resolved account ids for UI auto-suggest (FSERP-style erp-defaults)."""
    by = ensure_hotel_coa(tenant)
    purposes = []
    by_module: dict[str, list] = {}
    for p in HOTEL_COA_PURPOSES:
        acc = by.get(p.account_code)
        item = {
            'key': p.key,
            'module': p.module,
            'label': p.label,
            'account_code': p.account_code,
            'hint': p.hint,
            'account_id': acc.id if acc else None,
            'account_name': acc.account_name if acc else None,
        }
        purposes.append(item)
        by_module.setdefault(p.module, []).append(item)

    codes = {
        code: {
            'id': acc.id,
            'code': acc.account_code,
            'name': acc.account_name,
            'account_type': acc.account_type,
            'book': acc.book or '',
            'is_group': acc.is_group,
        }
        for code, acc in by.items()
        if not acc.is_group
    }

    settlement_ids = []
    for code in SETTLEMENT_PREFERENCE:
        acc = by.get(code)
        if acc:
            settlement_ids.append(acc.id)

    return {
        'purposes': purposes,
        'by_module': by_module,
        'codes': codes,
        'settlement_preference': list(SETTLEMENT_PREFERENCE),
        'settlement_account_ids': settlement_ids,
        'suggestions': {
            'expense': purpose_row(by, 'expense.general'),
            'purchases': purpose_row(by, 'expense.purchases'),
            'rent': purpose_row(by, 'expense.rent'),
            'income_room': purpose_row(by, 'income.room'),
            'income_fnb': purpose_row(by, 'income.fnb'),
            'income_other': purpose_row(by, 'income.other'),
            'ar': purpose_row(by, 'ar.guests'),
            'ap': purpose_row(by, 'ap.trade'),
            'cash': purpose_row(by, 'bank.cash'),
            'bank': purpose_row(by, 'bank.operating'),
            'loan_borrowed_principal': purpose_row(by, 'loan.principal_pay'),
            'loan_lent_principal': purpose_row(by, 'loan.principal_recv'),
            'loan_interest_expense': purpose_row(by, 'expense.interest_loan'),
            'loan_interest_income': purpose_row(by, 'income.interest_loan'),
            'voucher_payment': purpose_row(by, 'voucher.payment_expense'),
            'voucher_receipt': purpose_row(by, 'voucher.receipt_income'),
            'budget_expense': purpose_row(by, 'budget.expense'),
            'budget_revenue': purpose_row(by, 'budget.revenue'),
        },
    }


def purpose_row(by: dict, key: str) -> dict[str, Any] | None:
    code = purpose_code(key)
    if not code:
        return None
    acc = by.get(code)
    if not acc:
        return None
    return {
        'key': key,
        'account_code': code,
        'account_id': acc.id,
        'account_name': acc.account_name,
        'label': f'{code} — {acc.account_name}',
    }
