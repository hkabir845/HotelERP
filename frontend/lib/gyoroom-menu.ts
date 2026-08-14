import type { ModuleKey } from '@/lib/modules'

export type MenuItem = {
  title: string
  key?: string
  path?: string
  children?: MenuItem[]
  module?: ModuleKey
}

/** Left menubar copied from live GYOROOM Turag PMS (kabir@admin.com, Aug 2026). */
export function getGyoroomMenu(tenantName = 'Restaurant'): MenuItem[] {
  return [
    { title: 'Dashboard', path: '/home' },
    { title: 'Apps Center', path: '/apps' },
    {
      title: 'FRONTDESK',
      children: [
        {
          title: 'Booking',
          children: [
            { title: 'Add Reservation', path: '/frontdesk/reservations/new' },
            { title: 'Add Booking', path: '/frontdesk/bookings/new' },
            { title: 'Reservation List', path: '/frontdesk/reservations' },
            { title: 'Cancel-Void-No Show List', path: '/frontdesk/reservations/cancelled' },
            { title: 'Add Registration', path: '/frontdesk/registrations/new' },
            { title: 'Registration List', path: '/frontdesk/registrations' },
          ],
        },
        { title: 'Inhouse', path: '/frontdesk/inhouse' },
        {
          title: 'Arrival',
          children: [
            { title: 'Yesterday', path: '/frontdesk/arrivals/yesterday' },
            { title: 'Today', path: '/frontdesk/arrivals/today' },
            { title: 'Tomorrow', path: '/frontdesk/arrivals/tomorrow' },
            { title: 'This Week', path: '/frontdesk/arrivals/week' },
          ],
        },
        {
          title: 'Departure',
          children: [
            { title: 'Yesterday', path: '/frontdesk/departures/yesterday' },
            { title: 'Today', path: '/frontdesk/departures/today' },
            { title: 'Tomorrow', path: '/frontdesk/departures/tomorrow' },
          ],
        },
        { title: 'Pending Folios', path: '/frontdesk/pending-folio' },
        { title: 'Room Rack', path: '/frontdesk/room-rack' },
        { title: 'Room Rate Schedule', path: '/frontdesk/room-rate-schedule' },
        { title: 'Room Type Avl. Forecast', path: '/frontdesk/forecast/room-type' },
        { title: 'Room Availability Forecast', path: '/frontdesk/forecast/availability' },
        {
          title: 'Configurations',
          children: [
            { title: 'Package', path: '/frontdesk/config/packages' },
            { title: 'Room View Type', path: '/frontdesk/config/room-view-types' },
            { title: 'Bed Info', path: '/frontdesk/config/bed-info' },
            { title: 'Room Facility', path: '/frontdesk/config/room-facilities' },
            { title: 'Room Group', path: '/frontdesk/config/room-groups' },
            { title: 'Room Type', path: '/frontdesk/config/room-types' },
            { title: 'Room Type Special Rate', path: '/frontdesk/config/room-type-special-rates' },
            { title: 'Room', path: '/frontdesk/config/rooms' },
            { title: 'Extra Charge Items', path: '/frontdesk/config/extra-charge-items' },
            { title: 'Extra Charge Group', path: '/frontdesk/config/extra-charge-groups' },
            { title: 'Booking Agent', path: '/frontdesk/config/booking-agents' },
            { title: 'Company', path: '/frontdesk/config/companies' },
            { title: 'Rate Plan', path: '/frontdesk/config/rate-plans' },
            { title: 'Cancellation Rules', path: '/frontdesk/config/cancellation-rules' },
            { title: 'Board Type', path: '/frontdesk/config/board-types' },
            { title: 'Complimentary Options', path: '/frontdesk/config/complimentary-options' },
            { title: 'Guest Source', path: '/frontdesk/config/guest-sources' },
          ],
        },
        {
          title: 'Agent Fund Request',
          children: [
            { title: 'Create', path: '/frontdesk/agent-fund-requests/new' },
            { title: 'List', path: '/frontdesk/agent-fund-requests' },
          ],
        },
        {
          title: 'Reports',
          key: 'frontdesk-reports',
          children: [
            { title: 'Booking Report', path: '/reports/booking' },
            { title: 'Cancel/No-Show Report', path: '/reports/cancel-no-show' },
            { title: 'Arrival/Departure Summary', path: '/reports/arrival-departure-summary' },
            { title: 'Arrival/Departure Details', path: '/reports/arrival-departure-detail' },
            { title: 'Inhouse Summary', path: '/reports/inhouse-summary' },
            { title: 'Exp. Arr./Dep. Summary', path: '/reports/expected-arrival-departure-summary' },
            { title: 'Exp. Arr./Dep. Details', path: '/reports/expected-arrival-departure-detail' },
            { title: 'Daily Sales Report', path: '/reports/daily-sales' },
            { title: 'Booking Checklist Report', path: '/reports/booking-checklist' },
            { title: 'Pickup/Drop Report', path: '/reports/pickup-drop' },
            { title: 'Board Report', path: '/reports/board' },
            { title: 'Add-ons Report', path: '/reports/add-ons' },
            { title: 'Payout Report', path: '/reports/payout' },
            { title: 'Guest Report', path: '/reports/guest' },
            { title: 'Police Report', path: '/reports/police' },
            { title: 'Guest Due Report', path: '/reports/guest-due' },
            { title: 'Daily Occupied Room Info', path: '/reports/daily-occupied-rooms' },
            { title: 'Revenue Report', path: '/reports/revenue' },
            { title: 'Manager Report', path: '/reports/manager' },
            { title: 'Night Audit report', path: '/reports/night-audit' },
            { title: 'Income-Expense report', path: '/reports/income-expense' },
            { title: 'Monthly Sales Report', path: '/reports/monthly-sales' },
            { title: 'Agent Commission Report', path: '/reports/agent-commission' },
            { title: 'Daily Collection Report', path: '/reports/daily-collection' },
            { title: 'Monthly Collection Report', path: '/reports/monthly-collection' },
            { title: 'Userwise Daily Collection Rpt.', path: '/reports/userwise-daily-collection' },
            { title: 'Audit Trails Report', path: '/reports/audit-trail' },
          ],
        },
      ],
    },
    {
      title: 'HOUSEKEEPING',
      children: [
        { title: 'Room Status', path: '/housekeeping/room-status' },
        { title: 'Guest Status Report', path: '/housekeeping/guest-status-report' },
        {
          title: 'Amenity Distribution',
          children: [
            { title: 'Create', path: '/housekeeping/amenity-distribution/new' },
            { title: 'List', path: '/housekeeping/amenity-distribution' },
            { title: 'Report', path: '/housekeeping/amenity-distribution/report' },
          ],
        },
        { title: 'Maintenance and Block', path: '/housekeeping/maintenance-block' },
        { title: 'Task', path: '/housekeeping/tasks' },
        { title: 'Wake Up Call', path: '/housekeeping/wake-up-calls' },
        { title: 'Lost & Found', path: '/housekeeping/lost-found' },
        { title: 'Staff', path: '/housekeeping/staff' },
      ],
    },
    {
      title: 'BANQUET',
      children: [
        {
          title: 'Event',
          children: [
            { title: 'Create Event', path: '/banquet/events/new' },
            { title: 'Event List', path: '/banquet/events' },
          ],
        },
        { title: 'Pending Event Folios', path: '/banquet/pending-folios' },
        { title: 'Venue Availability Forecast', path: '/banquet/venue-forecast' },
        {
          title: 'Config',
          key: 'banquet-config',
          children: [
            { title: 'Venue', path: '/banquet/config/venues' },
            { title: 'External Vendor', path: '/banquet/config/vendors' },
            { title: 'Event Service', path: '/banquet/config/services' },
            { title: 'Individual Items', path: '/banquet/config/items' },
            { title: 'Set Menu (Package)', path: '/banquet/config/packages' },
            { title: 'Sessions', path: '/banquet/config/sessions' },
          ],
        },
        {
          title: 'Reports',
          key: 'banquet-reports',
          children: [
            { title: 'Event Report', path: '/banquet/reports/events' },
            { title: 'Service Report', path: '/banquet/reports/services' },
            { title: 'Individual Item Report', path: '/banquet/reports/items' },
            { title: 'Set Menu Report', path: '/banquet/reports/set-menu' },
          ],
        },
      ],
    },
    {
      title: 'F&B AND REVENUE CENTER',
      children: [
        {
          title: tenantName,
          children: [
            { title: 'New Order', path: '/fnb/orders/new' },
            { title: '[All] Active Order List', path: '/fnb/orders/active' },
            { title: '[Room Wise] Active Order List', path: '/fnb/orders/active-room-wise' },
            { title: 'Sales List', path: '/fnb/sales' },
          ],
        },
        { title: 'Sales List [All Service]', path: '/fnb/sales/all-service' },
        {
          title: 'Pos Customers',
          children: [
            {
              title: 'Due Receive',
              children: [
                { title: 'Create', path: '/fnb/pos-customer/due-receive/new' },
                { title: 'List', path: '/fnb/pos-customer/due-receive' },
              ],
            },
            { title: 'Customer', path: '/fnb/pos-customer/customers' },
            { title: 'Statement', path: '/fnb/pos-customer/statements' },
          ],
        },
        {
          title: 'Config',
          key: 'fnb-config',
          children: [
            { title: 'Revenue Center List', path: '/fnb/config/revenue-centers' },
            { title: 'Item', path: '/fnb/config/items' },
            { title: 'Category', path: '/fnb/config/categories' },
            { title: 'Sub-Category', path: '/fnb/config/sub-categories' },
            { title: 'Unit', path: '/fnb/config/units' },
            { title: 'Token', path: '/fnb/config/tokens' },
            { title: 'Serve By', path: '/fnb/config/serve-by' },
            { title: 'Take Away Agent', path: '/fnb/config/take-away-agents' },
          ],
        },
        {
          title: 'Expense Management',
          children: [
            { title: 'Expense Category', path: '/fnb/expenses/categories' },
            { title: 'Expense Head', path: '/fnb/expenses/heads' },
            { title: 'Expenses', path: '/fnb/expenses' },
          ],
        },
        { title: 'Guest Status Report', path: '/fnb/guest-status-report' },
        {
          title: 'Reports',
          key: 'fnb-reports',
          children: [
            { title: 'Revenue Center Sales Sheet', path: '/reports/fnb/sales-sheet' },
            { title: 'Item Wise Report', path: '/reports/fnb/item-wise' },
            { title: 'Cancel Report', path: '/reports/fnb/cancel' },
            { title: 'Userwise Collection Report', path: '/reports/fnb/userwise-collection' },
            { title: 'Expense Report', path: '/reports/fnb/expense' },
          ],
        },
      ],
    },
    {
      title: 'ACCOUNTS',
      children: [
        {
          title: 'Voucher',
          children: [
            { title: 'Cash Payment Voucher', path: '/accounts/vouchers/cash-payment' },
            { title: 'Bank Payment Voucher', path: '/accounts/vouchers/bank-payment' },
            { title: 'Cash Receipt Voucher', path: '/accounts/vouchers/cash-receipt' },
            { title: 'Bank Receipt Voucher', path: '/accounts/vouchers/bank-receipt' },
            { title: 'Contra Voucher', path: '/accounts/vouchers/contra' },
            { title: 'Journal Voucher', path: '/accounts/vouchers/journal' },
            { title: 'List of Voucher Entry', path: '/accounts/vouchers' },
          ],
        },
        {
          title: 'Head of Account',
          children: [
            { title: 'Account', path: '/accounts/chart-of-accounts/accounts' },
            { title: 'Group', path: '/accounts/chart-of-accounts/groups' },
            { title: 'Chart of Accounts', path: '/accounts/chart-of-accounts' },
          ],
        },
        { title: 'Corporate Loans', path: '/accounts/loans' },
        {
          title: 'Party Ledgers',
          children: [
            { title: 'All Parties', path: '/accounts/parties' },
            { title: 'Aging', path: '/accounts/parties/aging' },
            { title: 'Reconcile to Control', path: '/accounts/parties/reconcile' },
          ],
        },
        {
          title: 'Accounts Payable',
          children: [
            { title: 'Vendor Bills', path: '/accounts/payable' },
            { title: 'AP Payments', path: '/accounts/payable/payments' },
          ],
        },
        {
          title: 'Accounts Receivable',
          children: [
            { title: 'Customer Invoices', path: '/accounts/receivable' },
            { title: 'AR Receipts', path: '/accounts/receivable/payments' },
          ],
        },
        { title: 'Budgets', path: '/accounts/budgets' },
        {
          title: 'Reports',
          key: 'accounts-reports',
          children: [
            { title: 'Cash Book', path: '/reports/accounts/cash-book' },
            { title: 'Bank Book', path: '/reports/accounts/bank-book' },
            { title: 'General Ledger', path: '/reports/accounts/general-ledger' },
            { title: 'Group Ledger', path: '/reports/accounts/group-ledger' },
            { title: 'Opening Balance Report', path: '/reports/accounts/opening-balance' },
            { title: 'Accounts Balance Report', path: '/reports/accounts/account-balance' },
            { title: 'Expense Report', path: '/reports/accounts/expense' },
            { title: 'Transaction Details Report', path: '/reports/accounts/transaction-detail' },
            { title: 'Daily Cash Sheet Report', path: '/reports/accounts/daily-cash-sheet' },
            { title: 'Trial Balance', path: '/reports/accounts/trial-balance' },
            { title: 'Profit & Loss', path: '/reports/accounts/profit-loss' },
            { title: 'Balance Sheet', path: '/reports/accounts/balance-sheet' },
            { title: 'Party Aging', path: '/accounts/parties/aging' },
          ],
        },
      ],
    },
    {
      title: 'INVENTORY',
      children: [
        {
          title: 'Requisition',
          children: [
            { title: 'Add New', path: '/inventory/requisitions/new' },
            { title: 'Requisition List', path: '/inventory/requisitions' },
          ],
        },
        {
          title: 'Purchase & Purchase Return',
          children: [
            { title: 'Purchase', path: '/inventory/purchases/new' },
            { title: 'Return', path: '/inventory/purchases/return' },
            { title: 'Purchase/Return List', path: '/inventory/purchases' },
          ],
        },
        {
          title: 'Warehouse Transfer',
          children: [
            { title: 'Add New', path: '/inventory/warehouse-transfers/new' },
            { title: 'W.Transfer List', path: '/inventory/warehouse-transfers' },
          ],
        },
        {
          title: 'Stock Adjustment',
          children: [
            { title: 'Add', path: '/inventory/stock-adjustments/add' },
            { title: 'Remove', path: '/inventory/stock-adjustments/remove' },
            { title: 'Stock-Adjustment List', path: '/inventory/stock-adjustments' },
          ],
        },
        {
          title: 'Revenue Center Consumption',
          children: [
            { title: 'Create', path: '/inventory/revenue-center-consumption/new' },
            { title: 'List', path: '/inventory/revenue-center-consumption' },
          ],
        },
        {
          title: 'Amenities Consumption',
          children: [
            { title: 'Create', path: '/inventory/amenities-consumption/new' },
            { title: 'List', path: '/inventory/amenities-consumption' },
          ],
        },
        {
          title: 'Suppliers',
          children: [
            {
              title: 'Payment',
              children: [
                { title: 'Create', path: '/inventory/suppliers/payments/new' },
                { title: 'List', path: '/inventory/suppliers/payments' },
              ],
            },
            { title: 'Supplier List', path: '/inventory/suppliers' },
            { title: 'Supplier Statement', path: '/inventory/suppliers/statements' },
          ],
        },
        {
          title: 'Config',
          key: 'inventory-config',
          children: [
            { title: 'Item', path: '/inventory/config/items' },
            { title: 'Category', path: '/inventory/config/categories' },
            { title: 'Unit', path: '/inventory/config/units' },
            { title: 'Warehouse', path: '/inventory/config/warehouses' },
          ],
        },
        {
          title: 'Reports',
          key: 'inventory-reports',
          children: [
            { title: 'Current Stock', path: '/reports/inventory/current-stock' },
            { title: 'Stock Register', path: '/reports/inventory/stock-register' },
            { title: 'Inventory Report', path: '/reports/inventory/inventory' },
            { title: 'Purchase Report', path: '/reports/inventory/purchase' },
            { title: 'Warehouse Transfer Report', path: '/reports/inventory/warehouse-transfer' },
            { title: 'Item Wise Purchase Summary', path: '/reports/inventory/item-wise-purchase' },
            { title: 'Cost of Consumption Report', path: '/reports/inventory/cost-of-consumption' },
          ],
        },
      ],
    },
    {
      title: 'SALES & MARKETING',
      children: [
        {
          title: 'CRM',
          children: [
            { title: 'Quotation', path: '/crm/quotations' },
            { title: 'Invoice', path: '/crm/invoices' },
            { title: 'Leads', path: '/crm/leads' },
            { title: 'Lead Source', path: '/crm/lead-sources' },
            { title: 'Tasks', path: '/crm/tasks' },
          ],
        },
        {
          title: 'Analytics',
          children: [
            { title: 'Guest Analytics', path: '/crm/analytics/guests' },
            { title: 'Lead Analytics', path: '/crm/analytics/leads' },
          ],
        },
        { title: 'Guest Feedback', path: '/crm/feedback' },
        {
          title: 'Customers',
          children: [
            { title: 'Individuals', path: '/crm/customers/individuals' },
            { title: 'Companies', path: '/crm/customers/companies' },
          ],
        },
        {
          title: 'Follow-Up Schedulers',
          children: [
            { title: 'Next Follow-Up Tasks', path: '/crm/follow-up/tasks' },
            { title: 'Follow-Up Comments', path: '/crm/follow-up/comments' },
            { title: 'Checklist Report', path: '/crm/follow-up/checklists' },
            { title: 'Guest Frequency Report', path: '/crm/follow-up/guest-frequency' },
          ],
        },
      ],
    },
    {
      title: 'HUMAN RESOURCES',
      children: [
        { title: 'HR Dashboard', path: '/hr' },
        {
          title: 'HR Management',
          children: [
            { title: 'Employees', path: '/hr/employees' },
            { title: 'Branches', path: '/hr/branches' },
            { title: 'Departments', path: '/hr/departments' },
            { title: 'Designations', path: '/hr/designations' },
            { title: 'Work Shifts', path: '/hr/work-shifts' },
          ],
        },
        {
          title: 'Attendance',
          children: [
            { title: 'Punch In/Out', path: '/hr/attendance/punch' },
            { title: 'Attendence List', path: '/hr/attendance' },
          ],
        },
        {
          title: 'Leave & Holiday',
          children: [
            { title: 'Leave Management', path: '/hr/leave' },
            { title: 'Leave Requests', path: '/hr/leave-requests' },
            { title: 'Public Holidays', path: '/hr/holidays' },
          ],
        },
        {
          title: 'Payroll',
          children: [
            { title: 'Salary Structure', path: '/hr/salary-structure' },
            { title: 'Payroll Management', path: '/hr/payroll' },
            {
              title: 'Payment Management',
              children: [
                { title: 'Bulk Payment', path: '/hr/payroll/bulk-payment' },
                { title: 'Payment List', path: '/hr/payroll/payments' },
              ],
            },
          ],
        },
        {
          title: 'Loan Management',
          children: [
            { title: 'Loan List', path: '/hr/loans' },
            { title: 'Loan Approvals', path: '/hr/loans/approvals' },
          ],
        },
        { title: 'HR Settings', path: '/hr/settings' },
        {
          title: 'HR Reports',
          children: [
            { title: 'Monthly Attendance', path: '/hr/reports/monthly-attendance' },
            { title: 'Late Fine Report', path: '/hr/reports/late-fine' },
            { title: 'Employee Leave Report', path: '/hr/reports/leave' },
            { title: 'Payroll Report', path: '/hr/reports/payroll' },
            { title: 'Salary Payment Report', path: '/hr/reports/salary-payment' },
          ],
        },
      ],
    },
    {
      title: 'ASSET & MAINTANANCE',
      children: [
        {
          title: 'Asset & Maintanance',
          children: [
            { title: 'Type', path: '/assets/types' },
            { title: 'Category', path: '/assets/categories' },
            { title: 'Vendor', path: '/assets/vendors' },
            { title: 'Vendor Contract', path: '/assets/vendor-contracts' },
            { title: 'Asset', path: '/assets' },
            { title: 'Maintenance Request', path: '/assets/maintenance-requests' },
            { title: 'Task', path: '/assets/work-orders' },
          ],
        },
      ],
    },
    {
      title: 'BROADCAST MESSAGE',
      children: [
        {
          title: 'Broadcast',
          children: [
            { title: 'New Message', path: '/broadcast/new' },
            { title: 'List', path: '/broadcast' },
            { title: 'Sms Cost Report', path: '/broadcast/sms-cost' },
          ],
        },
      ],
    },
    { title: 'REPORT CENTER', path: '/reports' },
    {
      title: 'UTILITIES',
      children: [
        { title: 'Blog', path: '/utilities/blog' },
        {
          title: 'Property Info',
          children: [
            { title: 'Property Images', path: '/utilities/property/images' },
            { title: 'Nearby Terminal', path: '/utilities/property/terminals' },
            { title: 'Accepted Payment Method', path: '/utilities/property/payment-methods' },
          ],
        },
        {
          title: 'Utilities',
          children: [
            {
              title: 'Roles',
              children: [
                { title: 'Create', path: '/utilities/roles/new' },
                { title: 'List', path: '/utilities/roles' },
              ],
            },
            {
              title: 'User',
              children: [
                { title: 'Manage Users', path: '/utilities/users' },
                { title: 'User-Wise-Accounts-Config', path: '/utilities/users/account-permissions' },
              ],
            },
            { title: 'Settings', path: '/utilities/settings' },
            { title: 'Additional Configs', path: '/utilities/additional-configs' },
            { title: 'Activity Log', path: '/utilities/logs' },
            {
              title: 'Website Content Settings',
              children: [
                { title: 'Website Contents', path: '/website/content' },
                { title: 'Website Content Details', path: '/website' },
              ],
            },
            { title: 'Clear Cache', path: '/utilities/clear-cache' },
          ],
        },
      ],
    },
  ]
}
