export type Field = {
  key: string
  label: string
  type?: 'text' | 'number' | 'date' | 'datetime-local' | 'email' | 'textarea' | 'select'
  options?: { value: string; label: string }[]
}

export type ActionDef = {
  id: string
  label: string
  from?: string[]
}

export type OpsPreset = {
  kind: string
  subtitle: string
  endpoint?: string
  actionEndpoint?: (id: number) => string
  pending?: boolean
  postKind?: string
  fields: Field[]
  columns: { key: string; label: string }[]
  actions: ActionDef[]
  createStatus?: string
}

const eventActions: ActionDef[] = [
  { id: 'confirm', label: 'Confirm', from: ['enquiry', 'open', 'tentative', 'new'] },
  { id: 'start', label: 'Start', from: ['confirmed'] },
  { id: 'complete', label: 'Complete', from: ['in_progress', 'confirmed'] },
  { id: 'pay', label: 'Collect', from: ['enquiry', 'confirmed', 'in_progress', 'completed', 'unpaid', 'open'] },
  { id: 'cancel', label: 'Cancel', from: ['enquiry', 'open', 'tentative', 'confirmed', 'new'] },
]

const BANQUET_EVENT: OpsPreset = {
  kind: 'banquet_event',
  subtitle: 'Create and run banquet events through confirm, start, collect, and complete.',
  fields: [
    { key: 'title', label: 'Event name' },
    { key: 'location', label: 'Venue' },
    { key: 'scheduled_at', label: 'Event date', type: 'datetime-local' },
    { key: 'quantity', label: 'Pax', type: 'number' },
    { key: 'contact_name', label: 'Contact person' },
    { key: 'phone', label: 'Phone' },
    { key: 'amount', label: 'Quoted amount', type: 'number' },
    { key: 'notes', label: 'Menu / notes', type: 'textarea' },
  ],
  columns: [
    { key: 'reference', label: 'No.' },
    { key: 'title', label: 'Event' },
    { key: 'location', label: 'Venue' },
    { key: 'contact_name', label: 'Contact' },
    { key: 'quantity', label: 'Pax' },
    { key: 'amount', label: 'Amount' },
    { key: 'balance', label: 'Due' },
    { key: 'status', label: 'Status' },
  ],
  actions: eventActions,
}

const CRM_LEAD: OpsPreset = {
  kind: 'crm_lead',
  subtitle: 'Capture leads and move them: contact → qualify → convert.',
  fields: [
    { key: 'title', label: 'Lead / guest name' },
    { key: 'location', label: 'Company' },
    { key: 'phone', label: 'Phone' },
    { key: 'email', label: 'Email', type: 'email' },
    { key: 'amount', label: 'Expected value', type: 'number' },
    { key: 'scheduled_at', label: 'Next follow-up', type: 'date' },
    { key: 'notes', label: 'Requirement', type: 'textarea' },
  ],
  columns: [
    { key: 'reference', label: 'No.' },
    { key: 'title', label: 'Lead' },
    { key: 'location', label: 'Company' },
    { key: 'phone', label: 'Phone' },
    { key: 'amount', label: 'Value' },
    { key: 'status', label: 'Status' },
  ],
  actions: [
    { id: 'contact', label: 'Contacted', from: ['new', 'open'] },
    { id: 'qualify', label: 'Qualify', from: ['contacted', 'new'] },
    { id: 'convert', label: 'Convert', from: ['qualified', 'contacted'] },
    { id: 'lose', label: 'Lost', from: ['new', 'contacted', 'qualified'] },
  ],
}

const PRESETS: Record<string, OpsPreset> = {
  banquet_event: BANQUET_EVENT,
  crm_lead: CRM_LEAD,
  crm_quotation: {
    kind: 'crm_quotation',
    subtitle: 'Send quotations, accept them, then raise an invoice.',
    fields: [
      { key: 'title', label: 'Customer' },
      { key: 'location', label: 'Company' },
      { key: 'phone', label: 'Phone' },
      { key: 'amount', label: 'Quote amount', type: 'number' },
      { key: 'scheduled_at', label: 'Valid until', type: 'date' },
      { key: 'notes', label: 'Scope', type: 'textarea' },
    ],
    columns: [
      { key: 'reference', label: 'Quote #' },
      { key: 'title', label: 'Customer' },
      { key: 'amount', label: 'Amount' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'send', label: 'Send', from: ['draft', 'open'] },
      { id: 'accept', label: 'Accept', from: ['sent'] },
      { id: 'invoice', label: 'Make invoice', from: ['accepted', 'sent'] },
      { id: 'reject', label: 'Reject', from: ['draft', 'sent'] },
    ],
  },
  crm_invoice: {
    kind: 'crm_invoice',
    subtitle: 'Collect payment against CRM invoices.',
    fields: [
      { key: 'title', label: 'Customer' },
      { key: 'phone', label: 'Phone' },
      { key: 'amount', label: 'Invoice amount', type: 'number' },
      { key: 'scheduled_at', label: 'Due date', type: 'date' },
      { key: 'notes', label: 'Description', type: 'textarea' },
    ],
    columns: [
      { key: 'reference', label: 'Invoice' },
      { key: 'title', label: 'Customer' },
      { key: 'amount', label: 'Amount' },
      { key: 'paid_amount', label: 'Paid' },
      { key: 'balance', label: 'Due' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'pay', label: 'Collect', from: ['unpaid', 'open', 'sent', 'partial'] },
      { id: 'void', label: 'Void', from: ['unpaid', 'open'] },
    ],
  },
  crm_task: {
    kind: 'crm_task',
    subtitle: 'Follow-up tasks for sales and guest relations.',
    fields: [
      { key: 'title', label: 'Task' },
      { key: 'contact_name', label: 'Guest / lead' },
      { key: 'phone', label: 'Phone' },
      { key: 'scheduled_at', label: 'Due', type: 'datetime-local' },
      { key: 'notes', label: 'Details', type: 'textarea' },
    ],
    columns: [
      { key: 'title', label: 'Task' },
      { key: 'contact_name', label: 'Guest' },
      { key: 'scheduled_at', label: 'Due' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'start', label: 'Start', from: ['open', 'new'] },
      { id: 'complete', label: 'Done', from: ['open', 'in_progress', 'new'] },
      { id: 'cancel', label: 'Cancel', from: ['open', 'in_progress', 'new'] },
    ],
  },
  crm_feedback: {
    kind: 'crm_feedback',
    subtitle: 'Record guest feedback and close the loop.',
    fields: [
      { key: 'title', label: 'Guest' },
      { key: 'location', label: 'Room / outlet' },
      { key: 'quantity', label: 'Rating (1-5)', type: 'number' },
      { key: 'notes', label: 'Comments', type: 'textarea' },
    ],
    columns: [
      { key: 'title', label: 'Guest' },
      { key: 'location', label: 'Place' },
      { key: 'quantity', label: 'Rating' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'start', label: 'In review', from: ['open', 'new'] },
      { id: 'complete', label: 'Resolved', from: ['open', 'in_progress', 'new'] },
    ],
  },
  hr_leave: {
    kind: 'hr_leave',
    subtitle: 'Leave requests: approve or reject.',
    fields: [
      { key: 'title', label: 'Employee' },
      { key: 'location', label: 'Leave type' },
      { key: 'scheduled_at', label: 'From', type: 'date' },
      { key: 'quantity', label: 'Days', type: 'number' },
      { key: 'notes', label: 'Reason', type: 'textarea' },
    ],
    columns: [
      { key: 'title', label: 'Employee' },
      { key: 'location', label: 'Type' },
      { key: 'quantity', label: 'Days' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'approve', label: 'Approve', from: ['pending', 'open'] },
      { id: 'reject', label: 'Reject', from: ['pending', 'open'] },
    ],
  },
  hr_loan: {
    kind: 'hr_loan',
    subtitle: 'Staff loans: approve, disburse, then close.',
    fields: [
      { key: 'title', label: 'Employee' },
      { key: 'amount', label: 'Loan amount', type: 'number' },
      { key: 'quantity', label: 'Installments', type: 'number' },
      { key: 'scheduled_at', label: 'Request date', type: 'date' },
      { key: 'notes', label: 'Purpose', type: 'textarea' },
    ],
    columns: [
      { key: 'title', label: 'Employee' },
      { key: 'amount', label: 'Amount' },
      { key: 'paid_amount', label: 'Paid' },
      { key: 'balance', label: 'Due' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'approve', label: 'Approve', from: ['pending', 'open'] },
      { id: 'disburse', label: 'Disburse', from: ['approved'] },
      { id: 'pay', label: 'Repay', from: ['disbursed', 'approved'] },
      { id: 'reject', label: 'Reject', from: ['pending', 'open'] },
      { id: 'close', label: 'Close', from: ['disbursed', 'paid'] },
    ],
  },
  hr_payroll: {
    kind: 'hr_payroll',
    subtitle: 'Approve posts Dr Salaries / Cr Payable; Pay posts Dr Payable / Cr Bank (employee party ledger).',
    endpoint: '/hr/payroll',
    actionEndpoint: (id) => `/hr/payroll/${id}/action`,
    fields: [
      { key: 'title', label: 'Employee name' },
      { key: 'scheduled_at', label: 'Period start', type: 'date' },
      { key: 'amount', label: 'Base salary', type: 'number' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
    ],
    columns: [
      { key: 'reference', label: 'Payroll #' },
      { key: 'title', label: 'Employee' },
      { key: 'amount', label: 'Net pay' },
      { key: 'status', label: 'Status' },
      { key: 'notes', label: 'Period' },
    ],
    actions: [
      { id: 'approve', label: 'Approve', from: ['draft', 'pending'] },
      { id: 'pay', label: 'Pay', from: ['approved', 'draft'] },
      { id: 'cancel', label: 'Cancel', from: ['draft', 'pending', 'approved'] },
    ],
  },
  hr_punch: {
    kind: 'hr_punch',
    subtitle: 'Punch in/out for today. Use employee_id from HR Employees if names clash.',
    endpoint: '/hr/attendance',
    fields: [
      { key: 'employee_id', label: 'Employee ID' },
      { key: 'title', label: 'Employee name' },
      { key: 'notes', label: 'Note' },
    ],
    columns: [
      { key: 'title', label: 'Employee' },
      { key: 'scheduled_at', label: 'Date' },
      { key: 'notes', label: 'Punches' },
      { key: 'quantity', label: 'Hours' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'punch_in', label: 'Punch in' },
      { id: 'punch_out', label: 'Punch out' },
    ],
  },
  requisitions: {
    kind: 'requisitions',
    subtitle: 'Request stock, then approve and fulfill (adds to inventory).',
    endpoint: '/inventory/requisitions',
    actionEndpoint: (id) => `/inventory/requisitions/${id}/action`,
    fields: [
      { key: 'location', label: 'Department' },
      { key: 'title', label: 'Item needed' },
      { key: 'notes', label: 'Details', type: 'textarea' },
    ],
    columns: [
      { key: 'reference', label: 'Req #' },
      { key: 'location', label: 'Department' },
      { key: 'notes', label: 'Item' },
      { key: 'contact_name', label: 'Requested by' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'approve', label: 'Approve', from: ['pending'] },
      { id: 'fulfill', label: 'Fulfill', from: ['approved', 'pending'] },
      { id: 'reject', label: 'Reject', from: ['pending'] },
    ],
  },
  purchases: {
    kind: 'purchases',
    subtitle: 'Raise a purchase, confirm, then receive to increase stock.',
    endpoint: '/inventory/purchases',
    actionEndpoint: (id) => `/inventory/purchases/${id}/action`,
    fields: [
      { key: 'title', label: 'Supplier' },
      { key: 'notes', label: 'Item' },
      { key: 'quantity', label: 'Qty', type: 'number' },
      { key: 'amount', label: 'Amount', type: 'number' },
      { key: 'phone', label: 'Supplier phone' },
    ],
    columns: [
      { key: 'reference', label: 'PO #' },
      { key: 'title', label: 'Supplier' },
      { key: 'notes', label: 'Item' },
      { key: 'amount', label: 'Amount' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'confirm', label: 'Confirm', from: ['draft'] },
      { id: 'receive', label: 'Receive', from: ['draft', 'pending'] },
      { id: 'cancel', label: 'Cancel', from: ['draft', 'pending'] },
    ],
  },
  inventory_stock: {
    kind: 'inventory_stock',
    subtitle: 'Add or remove stock against an item name.',
    endpoint: '/inventory/stock',
    fields: [
      { key: 'title', label: 'Item name' },
      { key: 'quantity', label: 'Quantity', type: 'number' },
      { key: 'notes', label: 'Reason' },
    ],
    columns: [
      { key: 'reference', label: 'Code' },
      { key: 'title', label: 'Item' },
      { key: 'quantity', label: 'On hand' },
      { key: 'amount', label: 'Cost' },
      { key: 'status', label: 'Status' },
    ],
    actions: [],
  },
  inventory_transfer: {
    kind: 'inventory_transfer',
    subtitle: 'Move an item from one warehouse to another.',
    endpoint: '/inventory/transfers',
    fields: [
      { key: 'title', label: 'Item' },
      { key: 'location', label: 'From warehouse' },
      { key: 'contact_name', label: 'To warehouse' },
      { key: 'notes', label: 'Notes' },
    ],
    columns: [
      { key: 'reference', label: 'Transfer #' },
      { key: 'title', label: 'Item' },
      { key: 'location', label: 'Route' },
      { key: 'status', label: 'Status' },
    ],
    actions: [],
  },
  inventory_payment: {
    kind: 'inventory_payment',
    subtitle: 'Record a payment to a supplier.',
    endpoint: '/inventory/payments',
    fields: [
      { key: 'title', label: 'Supplier' },
      { key: 'amount', label: 'Amount', type: 'number' },
      { key: 'location', label: 'Method' },
      { key: 'notes', label: 'Reference' },
    ],
    columns: [
      { key: 'title', label: 'Supplier' },
      { key: 'amount', label: 'Amount' },
      { key: 'location', label: 'Method' },
      { key: 'status', label: 'Status' },
    ],
    actions: [],
  },
  inventory_consumption: {
    kind: 'inventory_consumption',
    subtitle: 'Issue stock to a revenue center or amenities (reduces on-hand).',
    endpoint: '/inventory/stock',
    fields: [
      { key: 'title', label: 'Item' },
      { key: 'quantity', label: 'Qty used', type: 'number' },
      { key: 'location', label: 'Outlet / room' },
      { key: 'notes', label: 'Notes' },
    ],
    columns: [
      { key: 'title', label: 'Item' },
      { key: 'quantity', label: 'On hand' },
      { key: 'status', label: 'Status' },
    ],
    actions: [],
  },
  fnb_item: {
    kind: 'fnb_item',
    subtitle: 'Menu items used on New Order.',
    endpoint: '/fnb/menu-items',
    fields: [
      { key: 'title', label: 'Item name' },
      { key: 'location', label: 'Category' },
      { key: 'amount', label: 'Price', type: 'number' },
      { key: 'notes', label: 'Description' },
    ],
    columns: [
      { key: 'title', label: 'Item' },
      { key: 'location', label: 'Category' },
      { key: 'amount', label: 'Price' },
      { key: 'status', label: 'Status' },
    ],
    actions: [],
  },
  fnb_expense: {
    kind: 'fnb_expense',
    subtitle: 'Record outlet expenses, then approve and pay.',
    fields: [
      { key: 'title', label: 'Expense' },
      { key: 'location', label: 'Head / category' },
      { key: 'amount', label: 'Amount', type: 'number' },
      { key: 'scheduled_at', label: 'Date', type: 'date' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
    ],
    columns: [
      { key: 'reference', label: 'No.' },
      { key: 'title', label: 'Expense' },
      { key: 'location', label: 'Head' },
      { key: 'amount', label: 'Amount' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'approve', label: 'Approve', from: ['open', 'pending'] },
      { id: 'pay', label: 'Pay', from: ['approved', 'open', 'pending'] },
      { id: 'reject', label: 'Reject', from: ['open', 'pending'] },
    ],
  },
  fnb_pos_customer: {
    kind: 'fnb_pos_customer',
    subtitle: 'POS customers and due collection.',
    fields: [
      { key: 'title', label: 'Customer' },
      { key: 'phone', label: 'Phone' },
      { key: 'amount', label: 'Due amount', type: 'number' },
      { key: 'notes', label: 'Notes' },
    ],
    columns: [
      { key: 'title', label: 'Customer' },
      { key: 'phone', label: 'Phone' },
      { key: 'amount', label: 'Due' },
      { key: 'paid_amount', label: 'Received' },
      { key: 'balance', label: 'Balance' },
      { key: 'status', label: 'Status' },
    ],
    actions: [
      { id: 'pay', label: 'Receive due', from: ['open', 'unpaid', 'new'] },
    ],
  },
}

const ALIASES: Record<string, string> = {
  banquet_events: 'banquet_event',
  banquet_events_new: 'banquet_event',
  banquet_pending_folio: 'banquet_event',
  'banquet_pending-folios': 'banquet_event',
  banquet_pending_folios: 'banquet_event',
  banquet_venue_forecast: 'banquet_event',
  'banquet_venue-forecast': 'banquet_event',
  crm_quotations: 'crm_quotation',
  crm_invoices: 'crm_invoice',
  crm_leads: 'crm_lead',
  crm_tasks: 'crm_task',
  crm_feedback: 'crm_feedback',
  crm_followup_task: 'crm_task',
  'crm_follow-up_tasks': 'crm_task',
  crm_follow_up_tasks: 'crm_task',
  crm_individual: 'crm_lead',
  crm_company: 'crm_quotation',
  crm_customers_individuals: 'crm_lead',
  crm_customers_companies: 'crm_quotation',
  hr_leave_request: 'hr_leave',
  'hr_leave-requests': 'hr_leave',
  hr_leave_requests: 'hr_leave',
  hr_loans: 'hr_loan',
  hr_loan_approval: 'hr_loan',
  hr_loans_approvals: 'hr_loan',
  hr_payroll: 'hr_payroll',
  hr_payroll_payment: 'hr_payroll',
  hr_bulk_payment: 'hr_payroll',
  'hr_payroll_payments': 'hr_payroll',
  'hr_payroll_bulk-payment': 'hr_payroll',
  hr_attendance_punch: 'hr_punch',
  hr_attendance: 'hr_punch',
  'inventory/requisitions/new': 'requisitions',
  'inventory_requisitions_new': 'requisitions',
  fnb_config_items: 'fnb_item',
  fnb_expenses: 'fnb_expense',
  fnb_expenses_heads: 'fnb_expense',
  fnb_expenses_categories: 'fnb_expense',
  'fnb_pos-customer_customers': 'fnb_pos_customer',
  'fnb_pos-customer_due-receive': 'fnb_pos_customer',
  'fnb_pos-customer_due-receive_new': 'fnb_pos_customer',
  'fnb_pos-customer_statements': 'fnb_pos_customer',
  inventory_stock_adjustments: 'inventory_stock',
  'inventory_stock-adjustments': 'inventory_stock',
  'inventory_stock-adjustments_add': 'inventory_stock',
  'inventory_stock-adjustments_remove': 'inventory_stock',
  'inventory_warehouse-transfers': 'inventory_transfer',
  'inventory_warehouse-transfers_new': 'inventory_transfer',
  'inventory_revenue-center-consumption': 'inventory_consumption',
  'inventory_revenue-center-consumption_new': 'inventory_consumption',
  'inventory_amenities-consumption': 'inventory_consumption',
  'inventory_amenities-consumption_new': 'inventory_consumption',
  inventory_suppliers_payments: 'inventory_payment',
  inventory_suppliers_payments_new: 'inventory_payment',
  'inventory_suppliers_payments': 'inventory_payment',
  'inventory_suppliers_payments_new': 'inventory_payment',
}

export function getOpsPreset(kind?: string): OpsPreset | null {
  if (!kind) return null
  const key = ALIASES[kind] || kind
  const preset = PRESETS[key]
  if (!preset) return null
  if (kind.includes('pending')) {
    return { ...preset, pending: true, subtitle: 'Events or bills with an outstanding balance.' }
  }
  if (kind.includes('remove')) {
    return { ...preset, postKind: 'remove', subtitle: 'Remove stock from an item.' }
  }
  return preset
}
