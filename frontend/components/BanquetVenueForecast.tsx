'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

type Cell = { date: string; state: 'available' | 'occupied'; label: string; count: number }
type Row = { venue_id: number; venue: string; capacity: number; cells: Cell[] }

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

export default function BanquetVenueForecast() {
  const [from, setFrom] = useState(iso(new Date()))
  const [to, setTo] = useState(iso(addDays(new Date(), 13)))
  const [dates, setDates] = useState<string[]>([])
  const [rows, setRows] = useState<Row[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get(`/banquet/forecast?from=${from}&to=${to}`)
      .then((res) => {
        setDates(res.data.dates || [])
        setRows(res.data.rows || [])
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Venue Availability Forecast</h1>
          <p className="mt-1 text-gray-600">
            Booked sessions on each venue by date. Free cells can take a new event.
          </p>
          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
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
            <button
              type="button"
              onClick={load}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
            >
              Refresh
            </button>
            <p className="text-xs text-slate-500">Green = free · Rose = booked session(s)</p>
          </div>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : rows.length === 0 ? (
              <p className="p-8 text-center text-slate-500">Add venues under Banquet → Config.</p>
            ) : (
              <table className="min-w-full text-xs">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="sticky left-0 z-10 bg-slate-50 px-3 py-2 text-left">Venue</th>
                    {dates.map((d) => (
                      <th key={d} className="px-2 py-2 text-center whitespace-nowrap">
                        {shortDate(d)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.venue_id} className="border-t">
                      <td className="sticky left-0 z-10 bg-white px-3 py-2 font-medium whitespace-nowrap">
                        {row.venue}
                        <span className="ml-1 font-normal text-slate-500">{row.capacity} pax</span>
                      </td>
                      {row.cells.map((cell) => (
                        <td
                          key={cell.date}
                          title={cell.label}
                          className={`px-2 py-2 text-center ${
                            cell.state === 'occupied'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-emerald-50 text-emerald-800'
                          }`}
                        >
                          {cell.state === 'occupied' ? `${cell.count} booked` : 'Free'}
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
