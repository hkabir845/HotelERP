'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Plus, RefreshCw } from 'lucide-react'

function money(n: any) {
  if (n === null || n === undefined || n === '') return '—'
  return formatMoney(n)
}

export default function BanquetEventList({
  title,
  subtitle,
  pending,
  createPath,
}: {
  title: string
  subtitle: string
  pending?: boolean
  createPath?: string
}) {
  const [items, setItems] = useState<any[]>([])
  const [summary, setSummary] = useState<Record<string, any>>({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [payId, setPayId] = useState<number | null>(null)
  const [payAmount, setPayAmount] = useState('')
  const [payMethod, setPayMethod] = useState('cash')

  const load = () => {
    setLoading(true)
    setError('')
    const qs = pending ? '?pending=1' : ''
    apiClient
      .get(`/banquet/events${qs}`)
      .then((res) => {
        setItems(res.data.items || [])
        setSummary(res.data.summary || {})
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [pending])

  const act = async (id: number, action: string, extra?: Record<string, any>) => {
    setError('')
    try {
      await apiClient.post(`/banquet/events/${id}/action`, { action, ...extra })
      setPayId(null)
      setPayAmount('')
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
              <p className="mt-1 text-gray-600">{subtitle}</p>
            </div>
            <div className="flex gap-2">
              <button type="button" onClick={load} className="rounded-lg border bg-white p-2 text-gray-600">
                <RefreshCw className="h-5 w-5" />
              </button>
              {createPath && (
                <Link
                  href={createPath}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
                >
                  <Plus className="h-4 w-4" />
                  Create event
                </Link>
              )}
            </div>
          </div>

          {error && <p className="mb-4 text-red-600">{error}</p>}

          {summary && Object.keys(summary).length > 0 && (
            <div className="mb-4 flex flex-wrap gap-4 text-sm">
              {Object.entries(summary).map(([key, value]) => (
                <div key={key} className="rounded-lg border bg-white px-4 py-2">
                  <div className="capitalize text-slate-500">{key.replace(/_/g, ' ')}</div>
                  <div className="font-semibold">
                    {typeof value === 'number' && key !== 'events' && key !== 'pax'
                      ? money(value)
                      : String(value)}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {['No.', 'Date', 'Event', 'Venue', 'Session', 'Pax', 'Total', 'Paid', 'Due', 'Status', 'Actions'].map(
                    (h) => (
                      <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">
                        {h}
                      </th>
                    )
                  )}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={11} className="px-4 py-10 text-center text-slate-500">
                      Loading…
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="px-4 py-10 text-center text-slate-500">
                      No events yet.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t align-top">
                      <td className="px-3 py-2">{row.number}</td>
                      <td className="px-3 py-2 whitespace-nowrap">{row.event_date}</td>
                      <td className="px-3 py-2">
                        <div>{row.name}</div>
                        <div className="text-xs text-slate-500">{row.contact_name || row.company || row.phone}</div>
                      </td>
                      <td className="px-3 py-2">{row.venue_name || '—'}</td>
                      <td className="px-3 py-2">{row.session_name || '—'}</td>
                      <td className="px-3 py-2">{row.pax}</td>
                      <td className="px-3 py-2 text-right">{money(row.total_amount)}</td>
                      <td className="px-3 py-2 text-right">{money(row.paid_amount)}</td>
                      <td className="px-3 py-2 text-right">{money(row.due)}</td>
                      <td className="px-3 py-2 capitalize">{row.status.replace('_', ' ')}</td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {row.can_confirm && (
                            <button
                              type="button"
                              onClick={() => act(row.id, 'confirm')}
                              className="rounded border px-2 py-1 text-indigo-700"
                            >
                              Confirm
                            </button>
                          )}
                          {row.can_start && (
                            <button
                              type="button"
                              onClick={() => act(row.id, 'start')}
                              className="rounded border px-2 py-1 text-indigo-700"
                            >
                              Start
                            </button>
                          )}
                          {row.can_complete && (
                            <button
                              type="button"
                              onClick={() => act(row.id, 'complete')}
                              className="rounded border px-2 py-1 text-emerald-700"
                            >
                              Complete
                            </button>
                          )}
                          {row.can_pay && (
                            <button
                              type="button"
                              onClick={() => {
                                setPayId(row.id)
                                setPayAmount(String(row.due || ''))
                              }}
                              className="rounded border px-2 py-1 text-emerald-700"
                            >
                              Collect
                            </button>
                          )}
                          {row.can_cancel && (
                            <button
                              type="button"
                              onClick={() => act(row.id, 'cancel')}
                              className="rounded border px-2 py-1 text-red-700"
                            >
                              Cancel
                            </button>
                          )}
                        </div>
                        {payId === row.id && (
                          <div className="mt-2 flex flex-wrap items-end gap-2">
                            <input
                              type="number"
                              min="0"
                              className="w-28 rounded border px-2 py-1"
                              value={payAmount}
                              onChange={(e) => setPayAmount(e.target.value)}
                            />
                            <select
                              className="rounded border px-2 py-1"
                              value={payMethod}
                              onChange={(e) => setPayMethod(e.target.value)}
                            >
                              <option value="cash">Cash</option>
                              <option value="card">Card</option>
                              <option value="bank">Bank</option>
                              <option value="mobile">Mobile</option>
                            </select>
                            <button
                              type="button"
                              onClick={() =>
                                act(row.id, 'pay', { amount: Number(payAmount), method: payMethod })
                              }
                              className="rounded bg-indigo-600 px-2 py-1 text-white"
                            >
                              Post
                            </button>
                            <button type="button" onClick={() => setPayId(null)} className="text-slate-500">
                              Close
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
