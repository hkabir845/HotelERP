import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const ASSET_MASTERS: Record<string, MasterDef> = {
  types: {
    kind: 'types',
    title: 'Asset Type',
    subtitle: 'Types used to classify assets (HVAC, furniture, IT).',
    fields: [
      { key: 'name', label: 'Type', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Type' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  categories: {
    kind: 'categories',
    title: 'Asset Category',
    subtitle: 'Categories and depreciation rate on the asset register.',
    fields: [
      { key: 'name', label: 'Category', required: true },
      { key: 'depreciation_rate', label: 'Depreciation %', type: 'number' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Category' },
      { key: 'depreciation_rate', label: 'Depreciation %' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  vendors: {
    kind: 'vendors',
    title: 'Asset Vendor',
    subtitle: 'Suppliers for purchase and maintenance contracts.',
    fields: [
      { key: 'name', label: 'Vendor', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'address', label: 'Address', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Vendor' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'vendor-contracts': {
    kind: 'vendor-contracts',
    title: 'Vendor Contract',
    subtitle: 'AMC / supply contracts against an asset vendor.',
    fields: [
      { key: 'vendor_id', label: 'Vendor', type: 'select', optionsKey: 'vendors', required: true },
      { key: 'title', label: 'Contract', required: true },
      { key: 'start_date', label: 'Start', type: 'date' },
      { key: 'end_date', label: 'End', type: 'date' },
      { key: 'amount', label: 'Amount', type: 'number' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'vendor_name', label: 'Vendor' },
      { key: 'title', label: 'Contract' },
      { key: 'start_date', label: 'Start' },
      { key: 'end_date', label: 'End' },
      { key: 'amount', label: 'Amount' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const UTIL_MASTERS: Record<string, MasterDef> = {
  blog: {
    kind: 'blog',
    title: 'Blog',
    subtitle: 'Property blog posts for the public website.',
    fields: [
      { key: 'title', label: 'Title', required: true },
      { key: 'published_at', label: 'Publish date', type: 'date' },
      { key: 'is_published', label: 'Published', type: 'checkbox' },
      { key: 'body', label: 'Body', type: 'textarea' },
    ],
    columns: [
      { key: 'title', label: 'Title' },
      { key: 'published_at', label: 'Date' },
      { key: 'is_published', label: 'Published' },
    ],
  },
  images: {
    kind: 'images',
    title: 'Property Images',
    subtitle: 'Gallery URLs shown on the public property page.',
    fields: [
      { key: 'caption', label: 'Caption' },
      { key: 'image_url', label: 'Image URL', required: true },
      { key: 'sort_order', label: 'Sort', type: 'number' },
      ...yesNo,
    ],
    columns: [
      { key: 'caption', label: 'Caption' },
      { key: 'image_url', label: 'URL' },
      { key: 'sort_order', label: 'Sort' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  terminals: {
    kind: 'terminals',
    title: 'Nearby Terminal',
    subtitle: 'Airports, stations, and distances from the property.',
    fields: [
      { key: 'name', label: 'Terminal', required: true },
      { key: 'kind', label: 'Kind', type: 'select', optionsKey: 'terminal_kinds' },
      { key: 'distance_km', label: 'Distance (km)', type: 'number' },
      { key: 'notes', label: 'Notes' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Terminal' },
      { key: 'kind', label: 'Kind' },
      { key: 'distance_km', label: 'Km' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'payment-methods': {
    kind: 'payment-methods',
    title: 'Accepted Payment Method',
    subtitle: 'Payment methods advertised for the property.',
    fields: [
      { key: 'name', label: 'Method', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Method' },
      { key: 'description', label: 'Notes' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  roles: {
    kind: 'roles',
    title: 'Roles',
    subtitle: 'Named roles with module notes. Assign users under Manage Users.',
    fields: [
      { key: 'name', label: 'Role', required: true },
      { key: 'modules', label: 'Modules / permissions' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Role' },
      { key: 'modules', label: 'Modules' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}
