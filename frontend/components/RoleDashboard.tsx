'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute, { useRoleDashboardGate } from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { formatMoney } from '@/lib/money'
import { resolveRole, type HotelRole } from '@/lib/rbac'
import { roomTileFill, ROOM_STATUS_LABEL } from '@/lib/gyoroom-theme'
import {
  Bed,
  Calendar,
  ClipboardList,
  DollarSign,
  ShoppingCart,
  UtensilsCrossed,
  Wrench,
  ArrowRight,
  LayoutDashboard,
} from 'lucide-react'

type DashKey =
  | 'admin'
  | 'operations'
  | 'frontdesk'
  | 'housekeeping'
  | 'restaurant'
  | 'accountant'
  | 'purchase'

const DASH_META: Record<
  DashKey,
  { title: string; subtitle: string; roleHint: HotelRole | HotelRole[]; icon: typeof Bed }
> = {
  admin: {
    title: 'Property Dashboard',
    subtitle: 'Full-property overview for administrators',
    roleHint: 'admin',
    icon: LayoutDashboard,
  },
  operations: {
    title: 'Operations Dashboard',
    subtitle: 'Occupancy, F&B pulse, inventory & service quality',
    roleHint: ['operations_manager', 'manager', 'admin'],
    icon: Wrench,
  },
  frontdesk: {
    title: 'Front Desk Dashboard',
    subtitle: 'Arrivals, departures, in-house and room rack',
    roleHint: ['frontdesk', 'operations_manager', 'admin'],
    icon: Calendar,
  },
  housekeeping: {
    title: 'Housekeeping Dashboard',
    subtitle: 'Room status, tasks and lost & found',
    roleHint: ['housekeeping', 'maintenance', 'operations_manager', 'admin'],
    icon: Bed,
  },
  restaurant: {
    title: 'Restaurant Dashboard',
    subtitle: 'Orders, sales and revenue centers',
    roleHint: ['restaurant', 'fnb', 'operations_manager', 'admin'],
    icon: UtensilsCrossed,
  },
  accountant: {
    title: 'Accounts Dashboard',
    subtitle: 'Collections, ledgers and financial health',
    roleHint: ['accountant', 'admin'],
    icon: DollarSign,
  },
  purchase: {
    title: 'Purchase Dashboard',
    subtitle: 'Purchase orders, suppliers and stock levels',
    roleHint: ['purchase_officer', 'operations_manager', 'admin'],
    icon: ShoppingCart,
  },
}

interface DashStats {
  available: number
  occupied: number
  cleaning: number
  maintenance: number
  arrivals: number
  departures: number
  inhouse: number
  tasksPending: number
  lostFound: number
  ordersOpen: number
  fnbSales: number
  roomRevenue: number
  collection: number
  purchaseOpen: number
  rooms: Array<{ id: number; room_number: string; status: string }>
}

const empty: DashStats = {
  available: 0,
  occupied: 0,
  cleaning: 0,
  maintenance: 0,
  arrivals: 0,
  departures: 0,
  inhouse: 0,
  tasksPending: 0,
  lostFound: 0,
  ordersOpen: 0,
  fnbSales: 0,
  roomRevenue: 0,
  collection: 0,
  purchaseOpen: 0,
  rooms: [],
}

function QuickLink({ href, label, color }: { href: string; label: string; color: string }) {
  const router = useRouter()
  return (
    <button
      type="button"
      onClick={() => router.push(href)}
      className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3 text-left shadow-sm transition hover:shadow-md"
    >
      <span className="font-medium text-slate-800">{label}</span>
      <ArrowRight className="h-4 w-4" style={{ color }} />
    </button>
  )
}

function StatCard({
  label,
  value,
  color,
  onClick,
}: {
  label: string
  value: string | number
  color: string
  onClick?: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg px-4 py-3 text-left text-white shadow-sm transition hover:brightness-105"
      style={{ backgroundColor: color }}
    >
      <p className="text-xs font-medium uppercase tracking-wide opacity-90">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </button>
  )
}

export default function RoleDashboard({ dash }: { dash: DashKey }) {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  const meta = DASH_META[dash]
  const roleDef = resolveRole(user?.role)
  const hints = Array.isArray(meta.roleHint) ? meta.roleHint : [meta.roleHint]
  useRoleDashboardGate(hints as string[])
  const [stats, setStats] = useState<DashStats>(empty)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      const next = { ...empty }
      const mods = user?.enabled_modules || []
      const allow = (m: string) =>
        !user ||
        user.is_superuser ||
        (user.role || '').toLowerCase() === 'admin' ||
        mods.includes(m)
      try {
        const [rack, hkRooms, tasks, lf, sales, fnb] = await Promise.all([
          allow('frontdesk') ? apiClient.get('/frontdesk/room-rack').catch(() => null) : Promise.resolve(null),
          allow('housekeeping')
            ? apiClient.get('/housekeeping/rooms/status').catch(() => null)
            : Promise.resolve(null),
          allow('housekeeping') ? apiClient.get('/housekeeping/tasks').catch(() => null) : Promise.resolve(null),
          allow('housekeeping') ? apiClient.get('/housekeeping/lost-found').catch(() => null) : Promise.resolve(null),
          allow('frontdesk')
            ? apiClient
                .get('/frontdesk/reports/daily-sales', {
                  params: {
                    start: new Date().toISOString().slice(0, 10),
                    end: new Date().toISOString().slice(0, 10),
                  },
                })
                .catch(() => null)
            : Promise.resolve(null),
          allow('fnb')
            ? apiClient
                .get('/fnb/reports/sales-sheet', {
                  params: {
                    start: new Date().toISOString().slice(0, 10),
                    end: new Date().toISOString().slice(0, 10),
                  },
                })
                .catch(() => null)
            : Promise.resolve(null),
        ])

        // Prefer front-desk rack when available; else HK room-status (HK role has no frontdesk API).
        const roomSource = rack?.data?.rooms?.length ? rack.data : hkRooms?.data
        if (roomSource) {
          const summary = roomSource.summary || {}
          next.available = summary.available || 0
          next.occupied = summary.occupied || 0
          next.cleaning = summary.cleaning || 0
          next.maintenance = summary.maintenance || 0
          next.rooms = (roomSource.rooms || []).slice(0, 48).map((r: any) => ({
            id: r.id,
            room_number: r.room_number,
            status: r.status,
          }))
          const rooms = roomSource.rooms || []
          next.inhouse =
            rooms.filter((r: any) => r.current_reservation?.status === 'checked_in').length ||
            next.occupied
          if (rack?.data?.rooms) {
            const today = new Date().toISOString().slice(0, 10)
            next.arrivals = rooms.filter(
              (r: any) =>
                r.current_reservation?.check_in_date === today &&
                r.current_reservation?.status !== 'checked_in'
            ).length
            next.departures = rooms.filter((r: any) => r.current_reservation?.check_out_date === today).length
          }
        }

        if (tasks?.data?.tasks) {
          next.tasksPending = tasks.data.tasks.filter(
            (t: any) => t.status === 'pending' || t.status === 'in_progress'
          ).length
        }
        if (lf?.data?.items) next.lostFound = lf.data.items.length

        if (sales?.data?.rows?.length) {
          const row = sales.data.rows[sales.data.rows.length - 1]
          next.roomRevenue = Number(row.Total ?? row.total ?? row['Room revenue'] ?? 0) || 0
        } else if (sales?.data?.summary) {
          next.roomRevenue = Number(sales.data.summary.room_revenue || 0)
        }

        if (fnb?.data) {
          next.fnbSales = Number(fnb.data.summary?.total || 0)
          next.ordersOpen = Number(fnb.data.summary?.orders || 0)
          next.collection = Number(fnb.data.summary?.paid || 0)
        }

        try {
          if (allow('inventory')) {
            const inv = await apiClient.get('/inventory/stock').catch(() => null)
            if (inv?.data) {
              const rows = inv.data.items || inv.data.stock || inv.data.rows || []
              next.purchaseOpen = Array.isArray(rows) ? rows.length : Number(inv.data.summary?.items || 0)
            }
          }
        } catch {
          /* optional */
        }
      } finally {
        if (!cancelled) {
          setStats(next)
          setLoading(false)
        }
      }
    }
    load()
    const t = setInterval(load, 60000)
    return () => {
      cancelled = true
      clearInterval(t)
    }
  }, [dash, user])

  const Icon = meta.icon
  const accent = roleDef.color

  const links: Record<DashKey, { href: string; label: string }[]> = {
    admin: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/frontdesk/room-rack', label: 'Room Rack' },
      { href: '/frontdesk/reservations', label: 'Reservations' },
      { href: '/accounts/vouchers', label: 'Vouchers' },
    ],
    operations: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/frontdesk/room-rack', label: 'Room Rack' },
      { href: '/housekeeping/room-status', label: 'HK Board' },
      { href: '/fnb/orders/active', label: 'Restaurant Orders' },
    ],
    frontdesk: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/frontdesk/arrivals/today', label: "Today's Arrivals" },
      { href: '/frontdesk/room-rack', label: 'Room Rack' },
      { href: '/frontdesk/reservations/new', label: 'New Reservation' },
    ],
    housekeeping: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/housekeeping/room-status', label: 'Room Status' },
      { href: '/housekeeping/tasks', label: 'HK Tasks' },
      { href: '/housekeeping/lost-found', label: 'Lost & Found' },
    ],
    restaurant: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/fnb/orders/new', label: 'New Order / POS' },
      { href: '/fnb/orders/active', label: 'Active Orders' },
      { href: '/fnb/menus', label: 'Menu Items' },
    ],
    accountant: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/accounts/vouchers', label: 'Vouchers' },
      { href: '/accounts/chart-of-accounts', label: 'Chart of Accounts' },
      { href: '/accounts/parties', label: 'Party Ledgers' },
    ],
    purchase: [
      { href: '/apps', label: 'Apps Center' },
      { href: '/inventory/purchases', label: 'Purchase Orders' },
      { href: '/inventory/suppliers', label: 'Suppliers' },
      { href: '/inventory/requisitions', label: 'Requisitions' },
    ],
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen" style={{ background: '#f0f2f5' }}>
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto">
          <div className="p-6">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg p-2.5 text-white" style={{ backgroundColor: accent }}>
                  <Icon className="h-6 w-6" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">{meta.title}</h1>
                  <p className="text-sm text-slate-600">
                    {meta.subtitle}
                    {user?.role_label || roleDef.label
                      ? ` · Signed in as ${user?.role_label || roleDef.label}`
                      : ''}
                  </p>
                </div>
              </div>
              <div
                className="rounded-full px-3 py-1 text-xs font-semibold text-white"
                style={{ backgroundColor: accent }}
              >
                {user?.role_label || roleDef.label}
              </div>
            </div>

            {loading ? (
              <div className="flex h-48 items-center justify-center">
                <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-slate-700" />
              </div>
            ) : (
              <>
                {(dash === 'frontdesk' || dash === 'operations' || dash === 'admin' || dash === 'housekeeping') && (
                  <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
                    <StatCard label="Vacant" value={stats.available} color={roomTileFill('available')} onClick={() => router.push('/housekeeping/room-status')} />
                    <StatCard label="Occupied" value={stats.occupied} color={roomTileFill('occupied')} onClick={() => router.push(dash === 'housekeeping' ? '/housekeeping/room-status' : '/frontdesk/room-rack')} />
                    <StatCard label="Cleaning" value={stats.cleaning} color={roomTileFill('cleaning')} />
                    <StatCard label="Maintenance" value={stats.maintenance} color={roomTileFill('maintenance')} />
                    {dash !== 'housekeeping' && (
                      <>
                        <StatCard label="Arrivals" value={stats.arrivals} color="#ffc107" onClick={() => router.push('/frontdesk/arrivals/today')} />
                        <StatCard label="Departures" value={stats.departures} color="#17a2b8" onClick={() => router.push('/frontdesk/departures/today')} />
                      </>
                    )}
                    {dash === 'housekeeping' && (
                      <>
                        <StatCard label="Open tasks" value={stats.tasksPending} color="#059669" onClick={() => router.push('/housekeeping/tasks')} />
                        <StatCard label="Lost & found" value={stats.lostFound} color="#ff6b81" onClick={() => router.push('/housekeeping/lost-found')} />
                      </>
                    )}
                  </div>
                )}

                {(dash === 'frontdesk' || dash === 'operations' || dash === 'admin') && (
                  <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <StatCard label="In-house" value={stats.inhouse} color="#2563eb" />
                    <StatCard label="Room revenue (today)" value={formatMoney(stats.roomRevenue)} color="#28a745" />
                    <StatCard label="F&B collection" value={formatMoney(stats.collection)} color="#e83e8c" />
                  </div>
                )}

                {dash === 'operations' && (
                  <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <StatCard label="Open HK tasks" value={stats.tasksPending} color="#059669" onClick={() => router.push('/housekeeping/tasks')} />
                    <StatCard label="Lost & found items" value={stats.lostFound} color="#ff6b81" onClick={() => router.push('/housekeeping/lost-found')} />
                    <StatCard label="In-house rooms" value={stats.inhouse} color="#2563eb" />
                  </div>
                )}

                {(dash === 'restaurant' || dash === 'operations' || dash === 'admin') && (
                  <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <StatCard label="Orders today" value={stats.ordersOpen} color="#c2410c" onClick={() => router.push('/fnb/orders/active')} />
                    <StatCard label="F&B sales" value={formatMoney(stats.fnbSales)} color="#28a745" />
                    <StatCard label="Collected" value={formatMoney(stats.collection)} color="#7c3aed" />
                  </div>
                )}

                {(dash === 'accountant' || dash === 'admin') && (
                  <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <StatCard label="Room revenue" value={formatMoney(stats.roomRevenue)} color="#28a745" />
                    <StatCard label="F&B sales" value={formatMoney(stats.fnbSales)} color="#007bff" />
                    <StatCard label="Collections" value={formatMoney(stats.collection)} color="#e83e8c" />
                  </div>
                )}

                {(dash === 'purchase' || dash === 'operations') && (
                  <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <StatCard label="Stock alerts / items" value={stats.purchaseOpen} color="#b45309" onClick={() => router.push('/inventory/stock-adjustments')} />
                    <StatCard label="F&B demand signal" value={formatMoney(stats.fnbSales)} color="#c2410c" />
                  </div>
                )}

                {(dash === 'frontdesk' || dash === 'housekeeping' || dash === 'operations' || dash === 'admin') &&
                  stats.rooms.length > 0 && (
                    <div className="mb-6 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="mb-3 flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-slate-900">Room Status Board</h2>
                        <button
                          type="button"
                          className="text-sm font-medium text-blue-600"
                          onClick={() => router.push('/housekeeping/room-status')}
                        >
                          Open full board →
                        </button>
                      </div>
                      <div className="mb-3 flex flex-wrap gap-3 text-xs text-slate-600">
                        {['available', 'occupied', 'cleaning', 'maintenance', 'reserved'].map((s) => (
                          <span key={s} className="inline-flex items-center gap-1.5">
                            <span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: roomTileFill(s) }} />
                            {ROOM_STATUS_LABEL[s]}
                          </span>
                        ))}
                      </div>
                      <div className="grid grid-cols-6 gap-2 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12">
                        {stats.rooms.map((room) => (
                          <div
                            key={room.id}
                            className="rounded px-1 py-2 text-center text-xs font-bold text-white shadow-sm"
                            style={{ backgroundColor: roomTileFill(room.status) }}
                            title={`${room.room_number} · ${ROOM_STATUS_LABEL[room.status] || room.status}`}
                          >
                            {room.room_number}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                <div className="mb-2 flex items-center gap-2">
                  <ClipboardList className="h-5 w-5 text-slate-500" />
                  <h2 className="text-lg font-semibold text-slate-900">Quick actions</h2>
                </div>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {links[dash].map((l) => (
                    <QuickLink key={l.href} href={l.href} label={l.label} color={accent} />
                  ))}
                </div>

                {dash === 'purchase' && (
                  <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                    Separation of duties: Purchase Officers can raise and receive stock but cannot post GL vouchers — Accounts owns the ledger.
                  </p>
                )}
                {dash === 'accountant' && (
                  <p className="mt-4 rounded-lg border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-900">
                    You have voucher posting and COA rights. Purchasing remains with the Purchase Officer to preserve audit controls.
                  </p>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
