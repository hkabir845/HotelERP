/**
 * Industry Report Center catalog — aligned with OPERA Cloud report groups,
 * restaurant POS packs (Toast/Aloha-style), and HotelERP live routes.
 *
 * Visibility = product_type pack ∩ enabled_modules.
 * Hotel & resort always include F&B (in-built restaurant).
 */
import type { ModuleKey, ProductType } from '@/lib/modules'

export type ReportStatus = 'live' | 'planned'

export type ReportDef = {
  id: string
  title: string
  description: string
  path: string
  module: ModuleKey
  /** Which SaaS product packs may see this report */
  products: ProductType[]
  category: string
  status: ReportStatus
  /** OPERA / industry group label */
  industryGroup?: string
}

const STAY: ProductType[] = ['hotel', 'resort', 'mixed']
const ALL: ProductType[] = ['hotel', 'resort', 'restaurant', 'mixed']
const REST: ProductType[] = ['restaurant', 'hotel', 'resort', 'mixed']

function r(
  id: string,
  title: string,
  description: string,
  path: string,
  module: ModuleKey,
  products: ProductType[],
  category: string,
  status: ReportStatus = 'live',
  industryGroup?: string,
): ReportDef {
  return { id, title, description, path, module, products, category, status, industryGroup }
}

/** Full catalog — live paths are real screens; planned are industry-standard gaps. */
export const REPORTS_CATALOG: ReportDef[] = [
  // ——— Arrivals / Departures / In-house (OPERA) ———
  r('fd-arrivals-today', 'Arrivals — Today', 'Guests expected / arrived today.', '/frontdesk/arrivals/today', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
  r('fd-departures-today', 'Departures — Today', 'Guests expected to check out today.', '/frontdesk/departures/today', 'frontdesk', STAY, 'Front Office', 'live', 'Departures'),
  r('fd-inhouse', 'Guests In-House', 'Current in-house occupancy list.', '/frontdesk/inhouse', 'frontdesk', STAY, 'Front Office', 'live', 'Guests In-House'),
  r('fd-arrival-dep-summary', 'Arrival / Departure Summary', 'Summary statistics for arrivals and departures.', '/reports/arrival-departure-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
  r('fd-arrival-dep-detail', 'Arrival / Departure Detail', 'Detailed arrival and departure movements.', '/reports/arrival-departure-detail', 'frontdesk', STAY, 'Front Office', 'live', 'Arrivals'),
  r('fd-expected-ad-summary', 'Expected A/D Summary', 'Forecasted arrivals and departures.', '/reports/expected-arrival-departure-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Forecast'),
  r('fd-expected-ad-detail', 'Expected A/D Detail', 'Line-level expected arrival/departure.', '/reports/expected-arrival-departure-detail', 'frontdesk', STAY, 'Front Office', 'live', 'Forecast'),
  r('fd-inhouse-summary', 'In-House Summary', 'Occupancy summary for in-house guests.', '/reports/inhouse-summary', 'frontdesk', STAY, 'Front Office', 'live', 'Guests In-House'),
  r('fd-cancel-noshow', 'Cancel / No-Show', 'Cancellations and no-shows for audit.', '/reports/cancel-no-show', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
  r('fd-booking', 'Booking Report', 'Reservation booking analysis.', '/reports/booking', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
  r('fd-booking-checklist', 'Booking Checklist', 'Pre-arrival checklist status.', '/reports/booking-checklist', 'frontdesk', STAY, 'Front Office', 'live', 'Reservations'),
  r('fd-guest', 'Guest Report', 'Guest profiles and stay history.', '/reports/guest', 'frontdesk', STAY, 'Front Office', 'live', 'Profiles'),
  r('fd-police', 'Police / Authority Report', 'Guest register for authority submission.', '/reports/police', 'frontdesk', STAY, 'Front Office', 'live', 'Profiles'),
  r('fd-guest-due', 'Guest Due Report', 'Open guest balances / city ledger dues.', '/reports/guest-due', 'frontdesk', STAY, 'Front Office', 'live', 'Accounts Receivable'),
  r('fd-occupied-rooms', 'Daily Occupied Rooms', 'Rooms occupied by date.', '/reports/daily-occupied-rooms', 'frontdesk', STAY, 'Front Office', 'live', 'Statistics'),
  r('fd-pickup-drop', 'Pickup / Drop', 'Airport and local transfers.', '/reports/pickup-drop', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),
  r('fd-board', 'Board Report', 'Meal plan / board counts.', '/reports/board', 'frontdesk', STAY, 'Front Office', 'live', 'Statistics'),
  r('fd-addons', 'Add-ons Report', 'Extra services attached to stays.', '/reports/add-ons', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),
  r('fd-payout', 'Payout Report', 'Paid-outs to guests.', '/reports/payout', 'frontdesk', STAY, 'Front Office', 'live', 'Financials'),

  // ——— End of Day / Manager (OPERA) ———
  r('fd-night-audit', 'Night Audit', 'End-of-day close and control totals.', '/reports/night-audit', 'frontdesk', STAY, 'End of Day', 'live', 'End of Day'),
  r('fd-manager', 'Manager Report', 'Daily manager flash — occupancy, ADR, revenue.', '/reports/manager', 'frontdesk', STAY, 'End of Day', 'live', 'End of Day'),
  r('fd-revenue', 'Revenue Report', 'Room and other revenue analysis.', '/reports/revenue', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
  r('fd-daily-sales', 'Daily Sales', 'Day sales flash.', '/reports/daily-sales', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
  r('fd-monthly-sales', 'Monthly Sales', 'Month sales summary.', '/reports/monthly-sales', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Statistics'),
  r('fd-daily-collection', 'Daily Collection', 'Cashier collections for the day.', '/reports/daily-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
  r('fd-monthly-collection', 'Monthly Collection', 'Collections by month.', '/reports/monthly-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
  r('fd-userwise-collection', 'User-wise Daily Collection', 'Collections by cashier / user.', '/reports/userwise-daily-collection', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
  r('fd-income-expense', 'Income & Expense', 'Operational income vs expense snapshot.', '/reports/income-expense', 'frontdesk', STAY, 'Accounts', 'live', 'Financials'),
  r('fd-agent-commission', 'Agent Commission', 'Travel agent / OTA commission.', '/reports/agent-commission', 'frontdesk', STAY, 'Front Office', 'live', 'Commissions'),
  r('fd-audit-trail', 'Audit Trail', 'User activity and posting audit.', '/reports/audit-trail', 'frontdesk', STAY, 'Front Office', 'live', 'Miscellaneous'),

  // ——— Housekeeping ———
  r('hk-guest-status', 'HK Guest Status', 'Housekeeping guest / room status report.', '/housekeeping/guest-status-report', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),
  r('hk-amenity', 'Amenity Distribution', 'Amenity issue and stock report.', '/housekeeping/amenity-distribution/report', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),
  r('hk-room-status', 'Room Status Board', 'Live room status for HK.', '/housekeeping/rooms/status', 'housekeeping', STAY, 'Housekeeping', 'live', 'Housekeeping'),

  // ——— F&B / Restaurant (always for hotel & resort) ———
  r('fnb-sales-sheet', 'F&B Sales Sheet', 'Outlet / revenue-center sales sheet.', '/reports/fnb/sales-sheet', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
  r('fnb-item-wise', 'Item-wise Sales', 'Menu item performance.', '/reports/fnb/item-wise', 'fnb', REST, 'Food & Beverage', 'live', 'Statistics'),
  r('fnb-cancel', 'F&B Cancel Report', 'Voided / cancelled POS lines.', '/reports/fnb/cancel', 'fnb', REST, 'Food & Beverage', 'live', 'Miscellaneous'),
  r('fnb-userwise', 'F&B User-wise Collection', 'POS collections by cashier.', '/reports/fnb/userwise-collection', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
  r('fnb-expense', 'F&B Expense Report', 'Restaurant operating expenses.', '/reports/fnb/expense', 'fnb', REST, 'Food & Beverage', 'live', 'Financials'),
  r('fnb-guest-status', 'F&B Guest Status', 'In-house guest F&B status.', '/fnb/guest-status-report', 'fnb', STAY, 'Food & Beverage', 'live', 'Guests In-House'),
  r('fnb-pos-statement', 'POS Customer Statement', 'City-ledger POS customer statement.', '/fnb/pos-customer/statements', 'fnb', REST, 'Food & Beverage', 'live', 'Accounts Receivable'),
  r('fnb-hourly-sales', 'Hourly Sales Flash', 'Sales by hour for labor planning.', '/reports/coming-soon?id=fnb-hourly-sales', 'fnb', REST, 'Food & Beverage', 'planned', 'Statistics'),
  r('fnb-table-turn', 'Table Turn / Cover Report', 'Covers, average check, table turns.', '/reports/coming-soon?id=fnb-table-turn', 'fnb', REST, 'Food & Beverage', 'planned', 'Statistics'),
  r('fnb-recipe-cost', 'Recipe Cost Analysis', 'Theoretical vs actual food cost.', '/fnb/recipes', 'recipes', REST, 'Food & Beverage', 'live', 'Statistics'),

  // ——— Banquet / Events (OPERA Event / Catering) ———
  r('bq-events', 'Event Report', 'Banquet events list and revenue.', '/banquet/reports/events', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
  r('bq-services', 'Event Services', 'Services sold on events.', '/banquet/reports/services', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
  r('bq-items', 'Event Items', 'Banquet item consumption.', '/banquet/reports/items', 'banquet', STAY, 'Banquet & Events', 'live', 'Event Reports'),
  r('bq-set-menu', 'Set Menu Report', 'Set menus used on events.', '/banquet/reports/set-menu', 'banquet', STAY, 'Banquet & Events', 'live', 'Catering Configuration'),
  r('bq-forecast', 'Venue Forecast', 'Banquet venue occupancy forecast.', '/banquet/forecast', 'banquet', STAY, 'Banquet & Events', 'live', 'Forecast'),

  // ——— Accounts / Financials (OPERA Financials + ERP) ———
  r('ac-cash-book', 'Cash Book', 'Cash ledger with diggable sources.', '/reports/accounts/cash-book', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-bank-book', 'Bank Book', 'Bank ledger with diggable sources.', '/reports/accounts/bank-book', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-gl', 'General Ledger', 'Account movements and running balance.', '/reports/accounts/general-ledger', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-group-ledger', 'Group Ledger', 'Roll-up ledger for account groups.', '/reports/accounts/group-ledger', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-opening', 'Opening Balance', 'COA openings as of date + journals.', '/reports/accounts/opening-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-balance', 'Account Balance', 'Balances as of date.', '/reports/accounts/account-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-expense', 'Expense Report', 'Expense accounts for the period.', '/reports/accounts/expense', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-txn', 'Transaction Detail', 'All posted journal lines.', '/reports/accounts/transaction-detail', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-daily-cash', 'Daily Cash Sheet', 'Cash receipts and payments for a day.', '/reports/accounts/daily-cash-sheet', 'accounts', ALL, 'Accounts', 'live', 'End of Day'),
  r('ac-tb', 'Trial Balance', 'Debit/credit trial balance.', '/reports/accounts/trial-balance', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-pl', 'Profit & Loss', 'Income statement for the period.', '/reports/accounts/profit-loss', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-bs', 'Balance Sheet', 'Assets, liabilities, equity.', '/reports/accounts/balance-sheet', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-party-aging', 'Party Aging', 'AR/AP aging by party.', '/accounts/parties/aging', 'accounts', ALL, 'Accounts', 'live', 'Accounts Receivable'),
  r('ac-party-reconcile', 'Party ↔ Control Reconcile', 'Subsidiary vs control GL.', '/accounts/parties/reconcile', 'accounts', ALL, 'Accounts', 'live', 'Financials'),
  r('ac-party-ledgers', 'Party Ledgers', 'Guest / vendor / employee subledgers.', '/accounts/parties', 'accounts', ALL, 'Accounts', 'live', 'Accounts Receivable'),

  // ——— Inventory ———
  r('inv-current', 'Current Stock', 'On-hand stock by item/warehouse.', '/reports/inventory/current-stock', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-register', 'Stock Register', 'Item movement register.', '/reports/inventory/stock-register', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-inventory', 'Inventory Report', 'Inventory valuation snapshot.', '/reports/inventory/inventory', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-purchase', 'Purchase Report', 'Purchases in period.', '/reports/inventory/purchase', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-transfer', 'Warehouse Transfer', 'Inter-warehouse transfers.', '/reports/inventory/warehouse-transfer', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-item-purchase', 'Item-wise Purchase Summary', 'Purchases by item.', '/reports/inventory/item-wise-purchase', 'inventory', ALL, 'Inventory', 'live', 'Miscellaneous'),
  r('inv-cogs', 'Cost of Consumption', 'Consumption cost for outlets.', '/reports/inventory/cost-of-consumption', 'inventory', ALL, 'Inventory', 'live', 'Statistics'),
  r('inv-supplier-stmt', 'Supplier Statement', 'Supplier account statement.', '/inventory/suppliers/statements', 'inventory', ALL, 'Inventory', 'live', 'Accounts Receivable'),

  // ——— HR ———
  r('hr-attendance', 'Monthly Attendance', 'Attendance summary by employee.', '/hr/reports/monthly-attendance', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
  r('hr-late', 'Late Fine Report', 'Late punches and fines.', '/hr/reports/late-fine', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
  r('hr-leave', 'Leave Report', 'Leave taken vs entitlement.', '/hr/reports/leave', 'hr', STAY, 'Human Resources', 'live', 'Miscellaneous'),
  r('hr-payroll', 'Payroll Report', 'Payroll slips and totals.', '/hr/reports/payroll', 'hr', STAY, 'Human Resources', 'live', 'Financials'),
  r('hr-salary-pay', 'Salary Payment Report', 'Paid salary list.', '/hr/reports/salary-payment', 'hr', STAY, 'Human Resources', 'live', 'Financials'),

  // ——— CRM / Sales ———
  r('crm-guest-freq', 'Guest Frequency', 'Repeat guest frequency.', '/crm/follow-up/guest-frequency', 'crm', STAY, 'Sales & CRM', 'live', 'Sales Account'),
  r('crm-checklists', 'Follow-up Checklists', 'Sales follow-up checklist report.', '/crm/follow-up/checklists', 'crm', STAY, 'Sales & CRM', 'live', 'Activity'),

  // ——— Spa / Laundry / Pool / Channel (module-gated) ———
  r('spa-sales', 'Spa Sales Report', 'Spa & salon revenue by service.', '/reports/coming-soon?id=spa-sales', 'spa', STAY, 'Spa & Leisure', 'planned', 'Financials'),
  r('laundry-sales', 'Laundry Sales Report', 'Laundry POS revenue.', '/reports/coming-soon?id=laundry-sales', 'laundry', STAY, 'Spa & Leisure', 'planned', 'Financials'),
  r('pool-usage', 'Pool Booking Report', 'Pool bookings and utilization.', '/reports/coming-soon?id=pool-usage', 'pool', STAY, 'Spa & Leisure', 'planned', 'Statistics'),
  r('channel-pickup', 'Channel Pickup', 'OTA / channel booking pickup.', '/reports/coming-soon?id=channel-pickup', 'channel', STAY, 'Channel', 'planned', 'Yield Management'),

  // ——— Assets ———
  r('asset-maint', 'Maintenance History', 'Asset maintenance history.', '/assets/maintenance-history', 'assets', STAY, 'Assets', 'live', 'Miscellaneous'),
  r('asset-depr', 'Depreciation Report', 'Asset depreciation schedule.', '/assets/depreciation', 'assets', STAY, 'Assets', 'live', 'Financials'),

  // ——— Broadcast ———
  r('bc-sms-cost', 'SMS Cost Report', 'Broadcast SMS cost summary.', '/broadcast/sms-cost', 'broadcast', ALL, 'Communications', 'live', 'Miscellaneous'),

  // ——— Industry planned (OPERA statistics / yield) ———
  r('stat-adr-occupancy', 'ADR & Occupancy Statistics', 'Day / MTD / YTD ADR, occupancy, RevPAR.', '/reports/coming-soon?id=stat-adr-occupancy', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
  r('stat-market-segment', 'Market Segment Statistics', 'Revenue and rooms by market segment.', '/reports/coming-soon?id=stat-market-segment', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
  r('stat-source', 'Source of Business', 'Bookings by source / channel.', '/reports/coming-soon?id=stat-source', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
  r('stat-room-type', 'Room Type Statistics', 'Performance by room type.', '/reports/coming-soon?id=stat-room-type', 'frontdesk', STAY, 'Statistics & Yield', 'planned', 'Statistics'),
  r('forecast-availability', 'Availability Forecast', 'Room type availability forecast.', '/frontdesk/forecast/availability', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Forecast'),
  r('forecast-room-type', 'Room Type Forecast', 'Forecast by room type.', '/frontdesk/forecast/room-type', 'frontdesk', STAY, 'Statistics & Yield', 'live', 'Forecast'),
]

export const REPORT_CATEGORIES = [
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
] as const

export function filterReportsCatalog(opts: {
  productType?: ProductType | string | null
  enabledModules?: string[] | null
  module?: ModuleKey | 'all'
  category?: string | 'all'
  status?: ReportStatus | 'all'
  search?: string
}): ReportDef[] {
  const product = (opts.productType || 'hotel') as ProductType
  const modules = opts.enabledModules
  const q = (opts.search || '').trim().toLowerCase()

  return REPORTS_CATALOG.filter((rep) => {
    // SaaS product pack: restaurant never sees stay-only reports; hotel/resort include F&B
    if (!rep.products.includes(product)) return false
    if (modules && modules.length > 0 && !modules.includes(rep.module)) return false
    if (opts.module && opts.module !== 'all' && rep.module !== opts.module) return false
    if (opts.category && opts.category !== 'all' && rep.category !== opts.category) return false
    if (opts.status && opts.status !== 'all' && rep.status !== opts.status) return false
    if (q) {
      const hay = `${rep.title} ${rep.description} ${rep.category} ${rep.industryGroup || ''}`.toLowerCase()
      if (!hay.includes(q)) return false
    }
    return true
  })
}

export function reportsByCategory(reports: ReportDef[]): { category: string; reports: ReportDef[] }[] {
  const map = new Map<string, ReportDef[]>()
  for (const rep of reports) {
    const list = map.get(rep.category) || []
    list.push(rep)
    map.set(rep.category, list)
  }
  return REPORT_CATEGORIES.filter((c) => map.has(c)).map((category) => ({
    category,
    reports: map.get(category) || [],
  }))
}
