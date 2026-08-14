import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const CRM_MASTERS: Record<string, MasterDef> = {
  'lead-sources': {
    kind: 'lead-sources',
    title: 'Lead Source',
    subtitle: 'Where leads come from (walk-in, website, agent).',
    fields: [
      { key: 'name', label: 'Source', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Source' },
      { key: 'description', label: 'Notes' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  individuals: {
    kind: 'individuals',
    title: 'Customers — Individuals',
    subtitle: 'Individual CRM customers used on quotes, invoices, and leads.',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'address', label: 'Address', type: 'textarea' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  companies: {
    kind: 'companies',
    title: 'Customers — Companies',
    subtitle: 'Corporate CRM customers.',
    fields: [
      { key: 'name', label: 'Company', required: true },
      { key: 'contact_person', label: 'Contact' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'address', label: 'Address', type: 'textarea' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Company' },
      { key: 'contact_person', label: 'Contact' },
      { key: 'phone', label: 'Phone' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const CRM_ENDPOINT = '/crm/config'
