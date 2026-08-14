'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

type Cell = {
  date: string
  rate?: number
  special?: boolean
  available?: number
  occupied?: number
  blocked?: number
  total?: number
  state?: 'available' | 'occupied' | 'blocked'
}

type Row = {
  room_type?: string
  room_number?: string
  room_type_id?: number
  base_rate?: number
  total?: number
  floor?: number
  cells: Cell[]
}

function iso(d: Date) {
  return d.toISOString().slice(0, 10)
}

function addDays(d: Date, n: number) {
  const next = new Date(d)
  next.setDate(next.getDate() + n)
  return next
}

function shortDate(value: string) {
  const d = new Date(`${value}T00:00:00`)
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
}

export default function ForecastGridPage({
  title,
  subtitle,
  endpoint,
  mode,
}: {
  title: string
  subtitle: string
  endpoint: string
  mode: 'rate' | 'room-type' | 'room'
}) {
  const today = iso(new Date())
  const [from, setFrom] = useState(today)
  const [to, setTo] = useState(iso(addDays(new Date(), mode === 'room' ? 9 : 13)))
  const [planId, setPlanId] = useState('')
  const [plans, setPlans] = useState<{ id: number; name: string }[]>([])
  const [dates, setDates] = useState<string[]>([])
  const [rows, setRows] = useState<Row[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ from, to })
    if (mode === 'rate' && planId) params.set('rate_plan_id', planId)
    apiClient
      .get(`${endpoint}?${params.toString()}`)
      .then((res) => {
        setDates(res.data.dates || [])
        setRows(res.data.rows || [])
        if (res.data.options?.rate_plans) setPlans(res.data.options.rate_plans)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [endpoint])

  const cellClass = (cell: Cell) => {
    if (mode === 'rate') {
      return cell.special ? 'bg-amber-50 text-amber-900' : 'bg-white text-gray-800'
    }
    if (mode === 'room') {
      if (cell.state === 'occupied') return 'bg-rose-100 text-rose-800'
      if (cell.state === 'blocked') return 'bg-slate-200 text-slate-600'
      return 'bg-emerald-50 text-emerald-800'
    }
    const avail = cell.available ?? 0
    if (avail <= 0) return 'bg-rose-100 text-rose-800'
    if ((cell.occupied || 0) > 0) return 'bg-amber-50 text-amber-900'
    return 'bg-emerald-50 text-emerald-800'
  }

  const cellText = (cell: Cell) => {
    if (mode === 'rate') return cell.rate?.toLocaleString() ?? '—'
    if (mode === 'room') {
      if (cell.state === 'occupied') return 'O'
      if (cell.state === 'blocked') return 'B'
      return 'A'
    }
    return `${cell.available ?? 0}/${cell.total ?? 0}`
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-1 text-gray-600">{subtitle}</p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border border-gray-200 bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">From</span>
              <input
                type="date"
                className="rounded-lg border px-3 py-2"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">To</span>
              <input
                type="date"
                className="rounded-lg border px-3 py-2"
                value={to}
                onChange={(e) => setTo(e.target.value)}
              />
            </label>
            {mode === 'rate' && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Rate plan</span>
                <select
                  className="rounded-lg border px-3 py-2"
                  value={planId}
                  onChange={(e) => setPlanId(e.target.value)}
                >
                  <option value="">All / base rate</option>
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <button
              type="button"
              onClick={load}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
            >
              Refresh
            </button>
            {mode === 'room' && (
              <p className="text-xs text-slate-500">A = available · O = occupied · B = blocked</p>
            )}
            {mode === 'room-type' && (
              <p className="text-xs text-slate-500">Cell shows available / total rooms</p>
            )}
            {mode === 'rate' && (
              <p className="text-xs text-slate-500">Highlighted cells use a special rate</p>
            )}
          </div>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-4 overflow-auto rounded-xl border border-gray-200 bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : rows.length === 0 ? (
              <p className="p-8 text-center text-slate-500">
                No rooms or room types yet. Add them under Frontdesk → Configurations.
              </p>
            ) : (
              <table className="min-w-full text-xs">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="sticky left-0 z-10 bg-slate-50 px-3 py-2 text-left">
                      {mode === 'room' ? 'Room' : 'Room type'}
                    </th>
                    {dates.map((d) => (
                      <th key={d} className="px-2 py-2 text-center whitespace-nowrap">
                        {shortDate(d)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => (
                    <tr key={row.room_type_id || row.room_number || idx} className="border-t">
                      <td className="sticky left-0 z-10 bg-white px-3 py-2 font-medium whitespace-nowrap">
                        {mode === 'room' ? (
                          <span>
                            {row.room_number}
                            <span className="ml-1 font-normal text-slate-500">{row.room_type}</span>
                          </span>
                        ) : (
                          <span>
                            {row.room_type}
                            {row.base_rate != null && (
                              <span className="ml-1 font-normal text-slate-500">
                                base {row.base_rate.toLocaleString()}
                              </span>
                            )}
                          </span>
                        )}
                      </td>
                      {row.cells.map((cell) => (
                        <td
                          key={cell.date}
                          className={`px-2 py-2 text-center font-medium ${cellClass(cell)}`}
                          title={
                            mode === 'room-type'
                              ? `${cell.available} available, ${cell.occupied} occupied, ${cell.blocked} blocked`
                              : undefined
                          }
                        >
                          {cellText(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
