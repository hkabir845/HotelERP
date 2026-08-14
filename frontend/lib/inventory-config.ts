import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const INVENTORY_MASTERS: Record<string, MasterDef> = {
  categories: {
    kind: 'categories',
    title: 'Inventory Category',
    subtitle: 'Groups for store items (housekeeping, kitchen, amenities).',
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
  units: {
    kind: 'units',
    title: 'Unit',
    subtitle: 'Stock units (pcs, kg, litre).',
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
  warehouses: {
    kind: 'warehouses',
    title: 'Warehouse',
    subtitle: 'Stores that hold stock and receive purchases.',
    fields: [
      { key: 'name', label: 'Warehouse', required: true },
      { key: 'location', label: 'Location' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Warehouse' },
      { key: 'location', label: 'Location' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  items: {
    kind: 'items',
    title: 'Inventory Item',
    subtitle: 'Store items with unit, category, min stock, and cost.',
    fields: [
      { key: 'item_code', label: 'Item code' },
      { key: 'name', label: 'Item name', required: true },
      { key: 'category_id', label: 'Category', type: 'select', optionsKey: 'categories' },
      { key: 'unit', label: 'Unit', type: 'select', optionsKey: 'units', optionValue: 'name', required: true },
      { key: 'warehouse_id', label: 'Default warehouse', type: 'select', optionsKey: 'warehouses' },
      { key: 'supplier_id', label: 'Default supplier', type: 'select', optionsKey: 'suppliers' },
      { key: 'cost_price', label: 'Cost price', type: 'number' },
      { key: 'min_stock_level', label: 'Min stock', type: 'number' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'item_code', label: 'Code' },
      { key: 'name', label: 'Item' },
      { key: 'category_name', label: 'Category' },
      { key: 'unit', label: 'Unit' },
      { key: 'warehouse_name', label: 'Warehouse' },
      { key: 'current_stock', label: 'Stock' },
      { key: 'cost_price', label: 'Cost' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  suppliers: {
    kind: 'suppliers',
    title: 'Supplier',
    subtitle: 'Vendors for purchases, returns, and payments.',
    fields: [
      { key: 'name', label: 'Supplier', required: true },
      { key: 'contact_person', label: 'Contact person' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'address', label: 'Address', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Supplier' },
      { key: 'contact_person', label: 'Contact' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email' },
      { key: 'due_balance', label: 'Due' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const INVENTORY_ENDPOINT = '/inventory/config'
