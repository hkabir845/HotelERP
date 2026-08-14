"""Industry report catalog filtered by SaaS product_type ∩ enabled_modules.

Aligned with OPERA Cloud report groups + restaurant POS packs.
Hotel & resort always include F&B; restaurant-only excludes stay/frontdesk.
"""

STAY = ('hotel', 'resort', 'mixed')
ALL = ('hotel', 'resort', 'restaurant', 'mixed')
REST = ('restaurant', 'hotel', 'resort', 'mixed')

CATEGORIES = [
    'Front Office',
    'End of Day',
    'Housekeeping',
    'Food & Beverage',
    'Banquet & Events',
    'Accounts',
    'Inventory',
    'Human Resources',
    'Sales & CRM',
    'Spa & Leisure',
    'Channel',
    'Assets',
    'Communications',
    'Statistics & Yield',
]


def _r(id_, title, description, path, module, products, category, status='live', industry_group=None):
    return {
        'id': id_,
        'title': title,
        'description': description,
        'path': path,
        'module': module,
        'products': list(products),
        'category': category,
        'status': status,
        'industry_group': industry_group,
    }


# Keep in sync with frontend/lib/reports-catalog.ts
REPORTS_CATALOG = [
    _r('fd-arrivals-today', 'Arrivals — Today', 'Guests expected / arrived today.', '/frontdesk/arrivals/today', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
    _r('fd-departures-today', 'Departures — Today', 'Guests expected to check out today.', '/frontdesk/departures/today', 'frontdesk', STAY, 'Front Office', 'live', 'Departures'),
    _r('fd-inhouse', 'Guests In-House', 'Current in-house occupancy list.', '/frontdesk/inhouse', 'frontdesk', STAY, 'Front Office', 'live', 'Guests In-House'),
    _r('fd-arrival-dep-summary', 'Arrival / Departure Summary', 'Summary statistics for arrivals and departures.', '/reports/arrival-departure-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
    _r('fd-arrival-dep-detail', 'Arrival / Departure Detail', 'Detailed arrival and departure movements.', '/reports/arrival-departure-detail', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
    _r('fd-expected-ad-summary', 'Expected A/D Summary', 'Forecasted arrivals and departures.', '/reports/expected-arrival-departure-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Forecast'),
    _r('fd-expected-ad-detail', 'Expected A/D Detail', 'Line-level expected arrival/departure.', '/reports/expected-arrival-departure-detail', 'frontdesk', STAY, 'Front Office', 'live', 'Forecast'),
    _r('fd-inhouse-summary', 'In-House Summary', 'Occupancy summary for in-house guests.', '/reports/inhouse-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Guests In-House'),
    _r('fd-cancel-noshow', 'Cancel / No-Show', 'Cancellations and no-shows for audit.', '/reports/cancel-no-show', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
    _r('fd-booking', 'Booking Report', 'Reservation booking analysis.', '/reports/booking', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
    _r('fd-booking-checklist', 'Booking Checklist', 'Pre-arrival checklist status.', '/reports/booking-checklist', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
    _r('fd-guest', 'Guest Report', 'Guest profiles and stay history.', '/reports/guest', 'frontdesk', STAY, 'Front Office', 'live', 'Profiles'),
    _r('fd-police', 'Police / Authority Report', 'Guest register for authority submission.', '/reports/police', 'frontdesk', STAY, 'Front Office', 'live', 'Profiles'),
    _r('fd-guest-due', 'Guest Due Report', 'Open guest balances / city ledger dues.', '/reports/guest-due', 'frontdesk', STAY, 'Front Office', 'live', 'Accounts Receivable'),
    _r('fd-occupied-rooms', 'Daily Occupied Rooms', 'Rooms occupied by date.', '/reports/daily-occupied-rooms', 'frontdesk', STAY, 'Front Office', 'live', 'Statistics'),
    _r('fd-pickup-drop', 'Pickup / Drop', 'Airport and local transfers.', '/reports/pickup-drop', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),
    _r('fd-board', 'Board Report', 'Meal plan / board counts.', '/reports/board', 'frontdesk', STAY, 'Front Office', 'live', 'Statistics'),
    _r('fd-addons', 'Add-ons Report', 'Extra services attached to stays.', '/reports/add-ons', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),
    _r('fd-payout', 'Payout Report', 'Paid-outs to guests.', '/reports/payout', 'frontdesk', STAY, 'Front Office', 'live', 'Financials'),
    _r('fd-night-audit', 'Night Audit', 'End-of-day close and control totals.', '/reports/night-audit', 'frontdesk', STAY, 'End of Day', 'live', 'End of Day'),
    _r('fd-manager', 'Manager Report', 'Daily manager flash — occupancy, ADR, revenue.', '/reports/manager', 'frontdesk', STAY, 'End of Day', 'live', 'End of Day'),
    _r('fd-revenue', 'Revenue Report', 'Room and other revenue analysis.', '/reports/revenue', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
    _r('fd-daily-sales', 'Daily Sales', 'Day sales flash.', '/reports/daily-sales', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
    _r('fd-monthly-sales', 'Monthly Sales', 'Month sales summary.', '/reports/monthly-sales', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
    _r('fd-daily-collection', 'Daily Collection', 'Cashier collections for the day.', '/reports/daily-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
    _r('fd-monthly-collection', 'Monthly Collection', 'Collections by month.', '/reports/monthly-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
    _r('fd-userwise-collection', 'User-wise Daily Collection', 'Collections by cashier / user.', '/reports/userwise-daily-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
    _r('fd-income-expense', 'Income & Expense', 'Operational income vs expense snapshot.', '/reports/income-expense', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
    _r('fd-agent-commission', 'Agent Commission', 'Travel agent / OTA commission.', '/reports/agent-commission', 'frontdesk', STAY, 'Front Office', 'live', 'Commissions'),
    _r('fd-audit-trail', 'Audit Trail', 'User activity and posting audit.', '/reports/audit-trail', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),
    _r('hk-guest-status', 'HK Guest Status', 'Housekeeping guest / room status report.', '/housekeeping/guest-status-report', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),
    _r('hk-amenity', 'Amenity Distribution', 'Amenity issue and stock report.', '/housekeeping/amenity-distribution/report', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),
    _r('hk-room-status', 'Room Status Board', 'Live room status for HK.', '/housekeeping/rooms/status', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),
    _r('fnb-sales-sheet', 'F&B Sales Sheet', 'Outlet / revenue-center sales sheet.', '/reports/fnb/sales-sheet', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
    _r('fnb-item-wise', 'Item-wise Sales', 'Menu item performance.', '/reports/fnb/item-wise', 'fnb', REST, 'Food & Beverage', 'live', 'Statistics'),
    _r('fnb-cancel', 'F&B Cancel Report', 'Voided / cancelled POS lines.', '/reports/fnb/cancel', 'fnb', REST, 'Food & Beverage', 'live', 'Miscellaneous'),
    _r('fnb-userwise', 'F&B User-wise Collection', 'POS collections by cashier.', '/reports/fnb/userwise-collection', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
    _r('fnb-expense', 'F&B Expense Report', 'Restaurant operating expenses.', '/reports/fnb/expense', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
    _r('fnb-guest-status', 'F&B Guest Status', 'In-house guest F&B status.', '/fnb/guest-status-report', 'fnb', STAY, 'Food & Beverage', 'live', 'Guests In-House'),
    _r('fnb-pos-statement', 'POS Customer Statement', 'City-ledger POS customer statement.', '/fnb/pos-customer/statements', 'fnb', REST, 'Food & Beverage', 'live', 'Accounts Receivable'),
    _r('fnb-hourly-sales', 'Hourly Sales Flash', 'Sales by hour for labor planning.', '/reports/coming-soon?id=fnb-hourly-sales', 'fnb', REST, 'Food & Beverage', 'planned', 'Statistics'),
    _r('fnb-table-turn', 'Table Turn / Cover Report', 'Covers, average check, table turns.', '/reports/coming-soon?id=fnb-table-turn', 'fnb', REST, 'Food & Beverage', 'planned', 'Statistics'),
    _r('fnb-recipe-cost', 'Recipe Cost Analysis', 'Theoretical vs actual food cost.', '/fnb/recipes', 'recipes', REST, 'Food & Beverage', 'live', 'Statistics'),
    _r('bq-events', 'Event Report', 'Banquet events list and revenue.', '/banquet/reports/events', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
    _r('bq-services', 'Event Services', 'Services sold on events.', '/banquet/reports/services', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
    _r('bq-items', 'Event Items', 'Banquet item consumption.', '/banquet/reports/items', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
    _r('bq-set-menu', 'Set Menu Report', 'Set menus used on events.', '/banquet/reports/set-menu', 'banquet', STAY, 'Banquet & Events', 'live', 'Catering Configuration'),
    _r('bq-forecast', 'Venue Forecast', 'Banquet venue occupancy forecast.', '/banquet/forecast', 'banquet', STAY, 'Banquet & Events', 'live', 'Forecast'),
    _r('ac-cash-book', 'Cash Book', 'Cash ledger with diggable sources.', '/reports/accounts/cash-book', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-bank-book', 'Bank Book', 'Bank ledger with diggable sources.', '/reports/accounts/bank-book', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-gl', 'General Ledger', 'Account movements and running balance.', '/reports/accounts/general-ledger', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-group-ledger', 'Group Ledger', 'Roll-up ledger for account groups.', '/reports/accounts/group-ledger', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-opening', 'Opening Balance', 'COA openings as of date + journals.', '/reports/accounts/opening-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-balance', 'Account Balance', 'Balances as of date.', '/reports/accounts/account-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-expense', 'Expense Report', 'Expense accounts for the period.', '/reports/accounts/expense', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-txn', 'Transaction Detail', 'All posted journal lines.', '/reports/accounts/transaction-detail', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-daily-cash', 'Daily Cash Sheet', 'Cash receipts and payments for a day.', '/reports/accounts/daily-cash-sheet', 'accounts', ALL, 'Accounts', 'live', 'End of Day'),
    _r('ac-tb', 'Trial Balance', 'Debit/credit trial balance.', '/reports/accounts/trial-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-pl', 'Profit & Loss', 'Income statement for the period.', '/reports/accounts/profit-loss', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-bs', 'Balance Sheet', 'Assets, liabilities, equity.', '/reports/accounts/balance-sheet', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-party-aging', 'Party Aging', 'AR/AP aging by party.', '/accounts/parties/aging', 'accounts', ALL, 'Accounts', 'live', 'Accounts Receivable'),
    _r('ac-party-reconcile', 'Party ↔ Control Reconcile', 'Subsidiary vs control GL.', '/accounts/parties/reconcile', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
    _r('ac-party-ledgers', 'Party Ledgers', 'Guest / vendor / employee subledgers.', '/accounts/parties', 'accounts', ALL, 'Accounts', 'live', 'Accounts Receivable'),
    _r('inv-current', 'Current Stock', 'On-hand stock by item/warehouse.', '/reports/inventory/current-stock', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-register', 'Stock Register', 'Item movement register.', '/reports/inventory/stock-register', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-inventory', 'Inventory Report', 'Inventory valuation snapshot.', '/reports/inventory/inventory', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-purchase', 'Purchase Report', 'Purchases in period.', '/reports/inventory/purchase', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-transfer', 'Warehouse Transfer', 'Inter-warehouse transfers.', '/reports/inventory/warehouse-transfer', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-item-purchase', 'Item-wise Purchase Summary', 'Purchases by item.', '/reports/inventory/item-wise-purchase', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
    _r('inv-cogs', 'Cost of Consumption', 'Consumption cost for outlets.', '/reports/inventory/cost-of-consumption', 'inventory', ALL, 'Inventory', 'live', 'Statistics'),
    _r('inv-supplier-stmt', 'Supplier Statement', 'Supplier account statement.', '/inventory/suppliers/statements', 'inventory', ALL, 'Inventory', 'live', 'Accounts Receivable'),
    _r('hr-attendance', 'Monthly Attendance', 'Attendance summary by employee.', '/hr/reports/monthly-attendance', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
    _r('hr-late', 'Late Fine Report', 'Late punches and fines.', '/hr/reports/late-fine', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
    _r('hr-leave', 'Leave Report', 'Leave taken vs entitlement.', '/hr/reports/leave', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
    _r('hr-payroll', 'Payroll Report', 'Payroll slips and totals.', '/hr/reports/payroll', 'hr', STAY, 'Human Resources', 'live', 'Financials'),
    _r('hr-salary-pay', 'Salary Payment Report', 'Paid salary list.', '/hr/reports/salary-payment', 'hr', STAY, 'Human Resources', 'live', 'Financials'),
    _r('crm-guest-freq', 'Guest Frequency', 'Repeat guest frequency.', '/crm/follow-up/guest-frequency', 'crm', STAY, 'Sales & CRM', 'live', 'Sales Account'),
    _r('crm-checklists', 'Follow-up Checklists', 'Sales follow-up checklist report.', '/crm/follow-up/checklists', 'crm', STAY, 'Sales & CRM', 'live', 'Activity'),
    _r('spa-sales', 'Spa Sales Report', 'Spa & salon revenue by service.', '/reports/coming-soon?id=spa-sales', 'spa', STAY, 'Spa & Leisure', 'planned', 'Financials'),
    _r('laundry-sales', 'Laundry Sales Report', 'Laundry POS revenue.', '/reports/coming-soon?id=laundry-sales', 'laundry', STAY, 'Spa & Leisure', 'planned', 'Financials'),
    _r('pool-usage', 'Pool Booking Report', 'Pool bookings and utilization.', '/reports/coming-soon?id=pool-usage', 'pool', STAY, 'Spa & Leisure', 'planned', 'Statistics'),
    _r('channel-pickup', 'Channel Pickup', 'OTA / channel booking pickup.', '/reports/coming-soon?id=channel-pickup', 'channel', STAY, 'Channel', 'planned', 'Yield Management'),
    _r('asset-maint', 'Maintenance History', 'Asset maintenance history.', '/assets/maintenance-history', 'assets', STAY, 'Assets', 'live', 'Miscellaneous'),
    _r('asset-depr', 'Depreciation Report', 'Asset depreciation schedule.', '/assets/depreciation', 'assets', STAY, 'Assets', 'live', 'Financials'),
    _r('bc-sms-cost', 'SMS Cost Report', 'Broadcast SMS cost summary.', '/broadcast/sms-cost', 'broadcast', ALL, 'Communications', 'live', 'Miscellaneous'),
    _r('stat-adr-occupancy', 'ADR & Occupancy Statistics', 'Day / MTD / YTD ADR, occupancy, RevPAR.', '/reports/coming-soon?id=stat-adr-occupancy', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
    _r('stat-market-segment', 'Market Segment Statistics', 'Revenue and rooms by market segment.', '/reports/coming-soon?id=stat-market-segment', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
    _r('stat-source', 'Source of Business', 'Bookings by source / channel.', '/reports/coming-soon?id=stat-source', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
    _r('stat-room-type', 'Room Type Statistics', 'Performance by room type.', '/reports/coming-soon?id=stat-room-type', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
    _r('forecast-availability', 'Availability Forecast', 'Room type availability forecast.', '/frontdesk/forecast/availability', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Forecast'),
    _r('forecast-room-type', 'Room Type Forecast', 'Forecast by room type.', '/frontdesk/forecast/room-type', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Forecast'),
]

PRODUCT_LABELS = {
    'hotel': 'Hotel (includes restaurant)',
    'resort': 'Resort (includes restaurant)',
    'restaurant': 'Restaurant only',
    'mixed': 'Hotel + Restaurant',
}


def filter_reports_catalog(tenant, module=None, category=None, status=None, search=None):
    product = (getattr(tenant, 'product_type', None) or 'hotel').lower()
    modules = tenant.get_enabled_modules() if tenant else []
    q = (search or '').strip().lower()
    module = (module or '').strip().lower() or None
    category = (category or '').strip() or None
    status = (status or '').strip().lower() or None

    out = []
    for rep in REPORTS_CATALOG:
        if product not in rep['products']:
            continue
        if modules and rep['module'] not in modules:
            continue
        if module and module != 'all' and rep['module'] != module:
            continue
        if category and category != 'all' and rep['category'] != category:
            continue
        if status and status != 'all' and rep['status'] != status:
            continue
        if q:
            hay = f"{rep['title']} {rep['description']} {rep['category']} {rep.get('industry_group') or ''}".lower()
            if q not in hay:
                continue
        out.append(rep)
    return out


def catalog_payload(tenant, **filters):
    reports = filter_reports_catalog(tenant, **filters)
    by_cat = {}
    for rep in reports:
        by_cat.setdefault(rep['category'], []).append(rep)
    groups = [{'category': c, 'reports': by_cat[c]} for c in CATEGORIES if c in by_cat]
    product = (getattr(tenant, 'product_type', None) or 'hotel').lower()
    return {
        'product_type': product,
        'product_label': PRODUCT_LABELS.get(product, product),
        'enabled_modules': tenant.get_enabled_modules() if tenant else [],
        'includes_restaurant': product in ('hotel', 'resort', 'mixed', 'restaurant'),
        'includes_rooms': product in ('hotel', 'resort', 'mixed'),
        'total': len(reports),
        'live': sum(1 for r in reports if r['status'] == 'live'),
        'planned': sum(1 for r in reports if r['status'] == 'planned'),
        'categories': groups,
        'reports': reports,
    }
