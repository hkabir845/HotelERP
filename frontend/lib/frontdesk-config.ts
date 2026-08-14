export type MasterField = {
  key: string
  label: string
  type?: 'text' | 'number' | 'textarea' | 'select' | 'checkbox' | 'date' | 'email'
  optionsKey?: string
  optionValue?: 'id' | 'name'
  required?: boolean
  placeholder?: string
}

export type MasterColumn = { key: string; label: string }

export type MasterDef = {
  kind: string
  title: string
  subtitle: string
  fields: MasterField[]
  columns: MasterColumn[]
}

const yesNo = [
  { key: 'is_active', label: 'Active', type: 'checkbox' as const },
]

export const FRONTDESK_MASTERS: Record<string, MasterDef> = {
  packages: {
    kind: 'packages',
    title: 'Package',
    subtitle: 'Stay packages sold with a reservation (inclusions and price).',
    fields: [
      { key: 'name', label: 'Package name', required: true },
      { key: 'price', label: 'Price', type: 'number', required: true },
      { key: 'description', label: 'Inclusions / description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Package' },
      { key: 'price', label: 'Price' },
      { key: 'description', label: 'Inclusions' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'room-view-types': {
    kind: 'room-view-types',
    title: 'Room View Type',
    subtitle: 'Views assigned to rooms (river, garden, city…).',
    fields: [
      { key: 'name', label: 'View name', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'View' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'bed-info': {
    kind: 'bed-info',
    title: 'Bed Info',
    subtitle: 'Bed setups used on rooms (king, twin, extra bed…).',
    fields: [
      { key: 'name', label: 'Bed type', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Bed type' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'room-facilities': {
    kind: 'room-facilities',
    title: 'Room Facility',
    subtitle: 'Amenities listed on room types (AC, minibar, balcony…).',
    fields: [
      { key: 'name', label: 'Facility', required: true },
      { key: 'icon', label: 'Icon key' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Facility' },
      { key: 'icon', label: 'Icon' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'room-groups': {
    kind: 'room-groups',
    title: 'Room Group',
    subtitle: 'Groups for reporting and rate rules (cottage, suite wing…).',
    fields: [
      { key: 'name', label: 'Group name', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Group' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'room-types': {
    kind: 'room-types',
    title: 'Room Type',
    subtitle: 'Types used on reservations, rack, website, and rates.',
    fields: [
      { key: 'name', label: 'Type name', required: true },
      { key: 'base_rate', label: 'Base rate', type: 'number', required: true },
      { key: 'max_occupancy', label: 'Max occupancy', type: 'number', required: true },
      { key: 'extra_occupancy', label: 'Extra occupancy', type: 'number' },
      { key: 'extra_bed_rate', label: 'Extra bed rate', type: 'number' },
      { key: 'amenities', label: 'Amenities', type: 'textarea' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Type' },
      { key: 'base_rate', label: 'Base rate' },
      { key: 'max_occupancy', label: 'Occ.' },
      { key: 'extra_occupancy', label: 'Extra' },
      { key: 'extra_bed_rate', label: 'Extra bed' },
      { key: 'room_count', label: 'Rooms' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'room-type-special-rates': {
    kind: 'room-type-special-rates',
    title: 'Room Type Special Rate',
    subtitle: 'Seasonal or plan-specific rates. These override base rate on the schedule.',
    fields: [
      { key: 'room_type_id', label: 'Room type', type: 'select', optionsKey: 'room_types', required: true },
      { key: 'rate_plan_id', label: 'Rate plan', type: 'select', optionsKey: 'rate_plans' },
      { key: 'start_date', label: 'From', type: 'date', required: true },
      { key: 'end_date', label: 'To', type: 'date', required: true },
      { key: 'rate', label: 'Rate', type: 'number', required: true },
      { key: 'notes', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'room_type_name', label: 'Room type' },
      { key: 'rate_plan_name', label: 'Rate plan' },
      { key: 'start_date', label: 'From' },
      { key: 'end_date', label: 'To' },
      { key: 'rate', label: 'Rate' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  rooms: {
    kind: 'rooms',
    title: 'Room',
    subtitle: 'Physical rooms on the rack. Type, floor, view, and rack rate.',
    fields: [
      { key: 'room_number', label: 'Room number', required: true },
      { key: 'room_type_id', label: 'Room type', type: 'select', optionsKey: 'room_types', required: true },
      { key: 'floor', label: 'Floor', type: 'number' },
      { key: 'status', label: 'Status', type: 'select', optionsKey: 'room_statuses' },
      { key: 'bed_type', label: 'Bed', type: 'select', optionsKey: 'bed_info', optionValue: 'name' },
      { key: 'view', label: 'View', type: 'select', optionsKey: 'room_view_types', optionValue: 'name' },
      { key: 'rack_rate', label: 'Rack rate', type: 'number' },
      { key: 'smoking_allowed', label: 'Smoking allowed', type: 'checkbox' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'room_number', label: 'Room' },
      { key: 'room_type_name', label: 'Type' },
      { key: 'floor', label: 'Floor' },
      { key: 'status', label: 'Status' },
      { key: 'bed_type', label: 'Bed' },
      { key: 'view', label: 'View' },
      { key: 'rack_rate', label: 'Rack rate' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'extra-charge-groups': {
    kind: 'extra-charge-groups',
    title: 'Extra Charge Group',
    subtitle: 'Groups for extras posted to the folio (laundry, minibar…).',
    fields: [
      { key: 'name', label: 'Group name', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Group' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'extra-charge-items': {
    kind: 'extra-charge-items',
    title: 'Extra Charge Items',
    subtitle: 'Chargeable items posted from the reservation folio.',
    fields: [
      { key: 'name', label: 'Item name', required: true },
      { key: 'group_id', label: 'Group', type: 'select', optionsKey: 'extra_charge_groups' },
      { key: 'amount', label: 'Amount', type: 'number', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Item' },
      { key: 'group_name', label: 'Group' },
      { key: 'amount', label: 'Amount' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'booking-agents': {
    kind: 'booking-agents',
    title: 'Booking Agent',
    subtitle: 'Travel agents and OTAs used on reservations, with commission.',
    fields: [
      { key: 'name', label: 'Agent name', required: true },
      { key: 'contact_person', label: 'Contact person' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'commission_rate', label: 'Commission %', type: 'number' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Agent' },
      { key: 'contact_person', label: 'Contact' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email' },
      { key: 'commission_rate', label: 'Comm. %' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  companies: {
    kind: 'companies',
    title: 'Company',
    subtitle: 'Corporate accounts for billed reservations.',
    fields: [
      { key: 'name', label: 'Company', required: true },
      { key: 'contact_person', label: 'Contact person' },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'credit_limit', label: 'Credit limit', type: 'number' },
      { key: 'address', label: 'Address', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Company' },
      { key: 'contact_person', label: 'Contact' },
      { key: 'phone', label: 'Phone' },
      { key: 'credit_limit', label: 'Credit limit' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'rate-plans': {
    kind: 'rate-plans',
    title: 'Rate Plan',
    subtitle: 'Plans used with special rates (BAR, corporate, package).',
    fields: [
      { key: 'name', label: 'Plan name', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Plan' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'cancellation-rules': {
    kind: 'cancellation-rules',
    title: 'Cancellation Rules',
    subtitle: 'Charges applied when a booking is cancelled before check-in.',
    fields: [
      { key: 'name', label: 'Rule name', required: true },
      { key: 'hours_before_checkin', label: 'Hours before check-in', type: 'number' },
      { key: 'cancellation_charge_percentage', label: 'Charge %', type: 'number' },
      { key: 'cancellation_charge_amount', label: 'Fixed charge', type: 'number' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Rule' },
      { key: 'hours_before_checkin', label: 'Hours before' },
      { key: 'cancellation_charge_percentage', label: 'Charge %' },
      { key: 'cancellation_charge_amount', label: 'Fixed' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'board-types': {
    kind: 'board-types',
    title: 'Board Type',
    subtitle: 'Meal plans (room only, BB, MAP, AP) with extra charge.',
    fields: [
      { key: 'name', label: 'Board type', required: true },
      { key: 'additional_charge', label: 'Additional charge', type: 'number' },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Board' },
      { key: 'additional_charge', label: 'Extra charge' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'complimentary-options': {
    kind: 'complimentary-options',
    title: 'Complimentary Options',
    subtitle: 'Comps offered on a stay (fruit basket, late checkout…).',
    fields: [
      { key: 'name', label: 'Option', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Option' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'guest-sources': {
    kind: 'guest-sources',
    title: 'Guest Source',
    subtitle: 'How the guest found the property (walk-in, website, agent…).',
    fields: [
      { key: 'name', label: 'Source', required: true },
      { key: 'description', label: 'Description', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Source' },
      { key: 'description', label: 'Description' },
      { key: 'is_active', label: 'Active' },
    ],
  },
}

export const ROOM_STATUSES = [
  { id: 'available', name: 'Available' },
  { id: 'occupied', name: 'Occupied' },
  { id: 'reserved', name: 'Reserved' },
  { id: 'cleaning', name: 'Cleaning' },
  { id: 'maintenance', name: 'Maintenance' },
  { id: 'out_of_order', name: 'Out of order' },
]
