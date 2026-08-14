import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const BANQUET_MASTERS: Record<string, MasterDef> = {
  venues: {
    kind: 'venues',
    title: 'Venue',
    subtitle: 'Halls and outdoor spaces that can be booked for events.',
    fields: [
      { key: 'name', label: 'Venue', required: true },
      { key: 'code', label: 'Code' },
      { key: 'capacity', label: 'Capacity (pax)', type: 'number' },
      { key: 'hourly_rate', label: 'Hourly rate', type: 'number' },
      { key: 'description', label: 'Setup / notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Venue' },
      { key: 'code', label: 'Code' },
      { key: 'capacity', label: 'Capacity' },
      { key: 'hourly_rate', label: 'Hourly rate' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  vendors: {
    kind: 'vendors',
    title: 'External Vendor',
    subtitle: 'Outside suppliers booked onto an event (decor, DJ, photo).',
    fields: [
      { key: 'name', label: 'Vendor', required: true },
      { key: 'service_type', label: 'Service type' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'rate', label: 'Default rate', type: 'number' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Vendor' },
      { key: 'service_type', label: 'Type' },
      { key: 'phone', label: 'Phone' },
      { key: 'rate', label: 'Rate' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  services: {
    kind: 'services',
    title: 'Event Service',
    subtitle: 'Chargeable banquet services (decoration, AV, photography).',
    fields: [
      { key: 'name', label: 'Service', required: true },
      { key: 'unit_price', label: 'Unit price', type: 'number', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Service' },
      { key: 'unit_price', label: 'Price' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  items: {
    kind: 'items',
    title: 'Individual Items',
    subtitle: 'Extra chairs, tables, and equipment added to an event folio.',
    fields: [
      { key: 'name', label: 'Item', required: true },
      { key: 'unit', label: 'Unit' },
      { key: 'unit_price', label: 'Unit price', type: 'number', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Item' },
      { key: 'unit', label: 'Unit' },
      { key: 'unit_price', label: 'Price' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  packages: {
    kind: 'packages',
    title: 'Set Menu (Package)',
    subtitle: 'Per-pax menus billed on the event (buffet, cocktail).',
    fields: [
      { key: 'name', label: 'Set menu', required: true },
      { key: 'price_per_pax', label: 'Price per pax', type: 'number', required: true },
      { key: 'description', label: 'Inclusions', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Set menu' },
      { key: 'price_per_pax', label: 'Per pax' },
      { key: 'description', label: 'Inclusions' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  sessions: {
    kind: 'sessions',
    title: 'Sessions',
    subtitle: 'Time slots used on venue bookings (morning, lunch, dinner).',
    fields: [
      { key: 'name', label: 'Session', required: true },
      { key: 'start_time', label: 'Start (HH:MM)', placeholder: '12:00' },
      { key: 'end_time', label: 'End (HH:MM)', placeholder: '16:00' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Session' },
      { key: 'start_time', label: 'Start' },
      { key: 'end_time', label: 'End' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const BANQUET_ENDPOINT = '/banquet/config'
export const BANQUET_EVENT_TYPES = [
  { id: 'wedding', name: 'Wedding' },
  { id: 'conference', name: 'Conference' },
  { id: 'birthday', name: 'Birthday' },
  { id: 'corporate', name: 'Corporate' },
  { id: 'reception', name: 'Reception' },
  { id: 'other', name: 'Other' },
]
