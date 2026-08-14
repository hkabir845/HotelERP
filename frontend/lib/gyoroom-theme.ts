/** GYOROOM-style status & dashboard palette (Turag PMS reference). */

export const GYOROOM = {
  sidebar: '#2c3e50',
  sidebarAlt: '#34495e',
  pageBg: '#f0f2f5',
  card: '#ffffff',
  text: '#2c3e50',
  muted: '#6c757d',
  vacant: '#28a745',
  occupied: '#dc3545',
  reserved: '#007bff',
  expectedArrival: '#ffc107',
  expectedDeparture: '#17a2b8',
  dirty: '#ff6b81',
  cleaning: '#f1c40f',
  clean: '#1abc9c',
  maintenance: '#95a5a6',
  outOfOrder: '#6c757d',
  revenue: '#28a745',
  collection: '#e83e8c',
  adr: '#007bff',
  receipt: '#343a40',
  chart: '#6c5ce7',
  accent: '#3498db',
} as const

export type RoomStatusKey =
  | 'available'
  | 'occupied'
  | 'reserved'
  | 'cleaning'
  | 'maintenance'
  | 'out_of_order'
  | 'dirty'
  | 'clean'

/** Solid fill for room tiles / legend chips */
export const ROOM_STATUS_FILL: Record<string, string> = {
  available: GYOROOM.vacant,
  vacant: GYOROOM.vacant,
  occupied: GYOROOM.occupied,
  reserved: GYOROOM.reserved,
  cleaning: GYOROOM.cleaning,
  dirty: GYOROOM.dirty,
  clean: GYOROOM.clean,
  maintenance: GYOROOM.maintenance,
  out_of_order: GYOROOM.outOfOrder,
}

export const ROOM_STATUS_LABEL: Record<string, string> = {
  available: 'Vacant',
  vacant: 'Vacant',
  occupied: 'Occupied',
  reserved: 'Reserved',
  cleaning: 'Cleaning',
  dirty: 'Dirty',
  clean: 'Clean',
  maintenance: 'Maintenance',
  out_of_order: 'Out of Order',
}

/** Tailwind-friendly soft card styles for room boards */
export const ROOM_STATUS_SOFT: Record<
  string,
  { label: string; color: string; bgColor: string; borderColor: string; fill: string }
> = {
  available: {
    label: 'Vacant',
    color: 'text-emerald-800',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-300',
    fill: GYOROOM.vacant,
  },
  occupied: {
    label: 'Occupied',
    color: 'text-red-800',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-300',
    fill: GYOROOM.occupied,
  },
  reserved: {
    label: 'Reserved',
    color: 'text-blue-800',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-300',
    fill: GYOROOM.reserved,
  },
  cleaning: {
    label: 'Cleaning',
    color: 'text-amber-900',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-300',
    fill: GYOROOM.cleaning,
  },
  dirty: {
    label: 'Dirty',
    color: 'text-rose-800',
    bgColor: 'bg-rose-50',
    borderColor: 'border-rose-300',
    fill: GYOROOM.dirty,
  },
  clean: {
    label: 'Clean',
    color: 'text-teal-800',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-300',
    fill: GYOROOM.clean,
  },
  maintenance: {
    label: 'Maintenance',
    color: 'text-slate-700',
    bgColor: 'bg-slate-100',
    borderColor: 'border-slate-300',
    fill: GYOROOM.maintenance,
  },
  out_of_order: {
    label: 'Out of Order',
    color: 'text-gray-800',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-400',
    fill: GYOROOM.outOfOrder,
  },
}

export function roomStatusSoft(status: string) {
  return (
    ROOM_STATUS_SOFT[status] || {
      label: status,
      color: 'text-gray-700',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-300',
      fill: GYOROOM.maintenance,
    }
  )
}

export function roomTileFill(status: string) {
  return ROOM_STATUS_FILL[status] || GYOROOM.maintenance
}
