import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const FNB_MASTERS: Record<string, MasterDef> = {
  'revenue-centers': {
    kind: 'revenue-centers',
    title: 'Revenue Center',
    subtitle: 'Outlets that post F&B sales (restaurant, room service, banquet).',
    fields: [
      { key: 'name', label: 'Revenue center', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Center' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  categories: {
    kind: 'categories',
    title: 'Category',
    subtitle: 'Menu categories used on items and POS filters.',
    fields: [
      { key: 'name', label: 'Category', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Category' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'sub-categories': {
    kind: 'sub-categories',
    title: 'Sub-Category',
    subtitle: 'Sub-groups under a menu category.',
    fields: [
      { key: 'name', label: 'Sub-category', required: true },
      { key: 'category_id', label: 'Category', type: 'select', optionsKey: 'categories', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Sub-category' },
      { key: 'category_name', label: 'Category' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  units: {
    kind: 'units',
    title: 'Unit',
    subtitle: 'Sale units on menu items (pcs, plate, glass).',
    fields: [
      { key: 'name', label: 'Unit', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Unit' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  tokens: {
    kind: 'tokens',
    title: 'Token',
    subtitle: 'Kitchen / bar tokens printed with an order.',
    fields: [
      { key: 'name', label: 'Token', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Token' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'serve-by': {
    kind: 'serve-by',
    title: 'Serve By',
    subtitle: 'Waiters and servers assigned to F&B orders.',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'phone', label: 'Phone' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'take-away-agents': {
    kind: 'take-away-agents',
    title: 'Take Away Agent',
    subtitle: 'Delivery / takeaway agents and commission.',
    fields: [
      { key: 'name', label: 'Agent', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'commission_rate', label: 'Commission %', type: 'number' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Agent' },
      { key: 'phone', label: 'Phone' },
      { key: 'commission_rate', label: 'Comm. %' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  items: {
    kind: 'items',
    title: 'Item',
    subtitle: 'Menu items sold at POS. Price, unit, token, and revenue center.',
    fields: [
      { key: 'name', label: 'Item name', required: true },
      { key: 'price', label: 'Price', type: 'number', required: true },
      { key: 'cost', label: 'Cost', type: 'number' },
      { key: 'category', label: 'Category', type: 'select', optionsKey: 'categories', optionValue: 'name', required: true },
      { key: 'subcategory', label: 'Sub-category', type: 'select', optionsKey: 'sub_categories', optionValue: 'name' },
      { key: 'unit', label: 'Unit', type: 'select', optionsKey: 'units', optionValue: 'name' },
      { key: 'token', label: 'Token', type: 'select', optionsKey: 'tokens', optionValue: 'name' },
      { key: 'revenue_center', label: 'Revenue center', type: 'select', optionsKey: 'revenue_centers', optionValue: 'name' },
      { key: 'description', label: 'Description', type: 'textarea' },
      { key: 'is_available', label: 'Available', type: 'checkbox' },
    ],
    columns: [
      { key: 'name', label: 'Item' },
      { key: 'category', label: 'Category' },
      { key: 'subcategory', label: 'Sub-category' },
      { key: 'unit', label: 'Unit' },
      { key: 'token', label: 'Token' },
      { key: 'revenue_center', label: 'Center' },
      { key: 'price', label: 'Price' },
      { key: 'is_available', label: 'Available' },
    ],
  },
  'expense-categories': {
    kind: 'expense-categories',
    title: 'Expense Category',
    subtitle: 'Groups for F&B outlet expenses.',
    fields: [
      { key: 'name', label: 'Category', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Category' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'expense-heads': {
    kind: 'expense-heads',
    title: 'Expense Head',
    subtitle: 'Expense types posted against an F&B category.',
    fields: [
      { key: 'name', label: 'Head', required: true },
      { key: 'category_id', label: 'Category', type: 'select', optionsKey: 'expense_categories', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Head' },
      { key: 'category_name', label: 'Category' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  expenses: {
    kind: 'expenses',
    title: 'Expenses',
    subtitle: 'Outlet expenses posted by head, date, and revenue center.',
    fields: [
      { key: 'expense_date', label: 'Date', type: 'date', required: true },
      { key: 'head_id', label: 'Expense head', type: 'select', optionsKey: 'expense_heads', required: true },
      { key: 'amount', label: 'Amount', type: 'number', required: true },
      { key: 'revenue_center', label: 'Revenue center', type: 'select', optionsKey: 'revenue_centers', optionValue: 'name' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
    ],
    columns: [
      { key: 'expense_date', label: 'Date' },
      { key: 'category_name', label: 'Category' },
      { key: 'head_name', label: 'Head' },
      { key: 'revenue_center', label: 'Center' },
      { key: 'amount', label: 'Amount' },
      { key: 'notes', label: 'Notes' },
    ],
  },
  'pos-customers': {
    kind: 'pos-customers',
    title: 'POS Customer',
    subtitle: 'Credit customers for restaurant sales and due receive.',
    fields: [
      { key: 'name', label: 'Customer', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'credit_limit', label: 'Credit limit', type: 'number' },
      { key: 'address', label: 'Address', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Customer' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email' },
      { key: 'credit_limit', label: 'Credit limit' },
      { key: 'due_balance', label: 'Due' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const FNB_ENDPOINT = '/fnb/config'
