'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatKeyedNumber } from '@/lib/money'

function monthStart() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function FnbReportPage({
  kind,
  title,
  subtitle,
  hideDates,
  endpoint = '/fnb/reports',
}: {
  kind: string
  title: string
  subtitle: string
  hideDates?: boolean
  endpoint?: string
}) {
  const [from, setFrom] = useState(monthStart())
  const [to, setTo] = useState(today())
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<any[]>([])
  const [summary, setSummary] = useState<Record<string, any>>({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams()
    if (!hideDates) {
      params.set('from', from)
      params.set('to', to)
    }
    const qs = params.toString()
    apiClient
      .get(`${endpoint}/${kind}${qs ? `?${qs}` : ''}`)
      .then((res) => {
        setColumns(res.data.columns || [])
        setRows(res.data.rows || [])
        setSummary(res.data.summary || {})
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [kind, endpoint])

  const cellKeys = rows[0]
    ? Object.keys(rows[0]).filter((k) => k !== 'id')
    : []
  const headers = columns.length ? columns : cellKeys.map((k) => k.replace(/_/g, ' '))

  const cellsFor = (row: any) => {
    if (columns.length && cellKeys.length === columns.length) {
      return cellKeys.map((k) => row[k])
    }
    if (columns.length) return cellKeys.map((k) => row[k])
    return cellKeys.map((k) => row[k])
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-1 text-gray-600">{subtitle}</p>

          {!hideDates && (
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
                Run
              </button>
            </div>
          )}

          {error && <p className="mt-4 text-red-600">{error}</p>}

          {summary && Object.keys(summary).length > 0 && (
            <div className="mt-4 flex flex-wrap gap-4 text-sm">
              {Object.entries(summary).map(([key, value]) => (
                <div key={key} className="rounded-lg border bg-white px-4 py-2">
                  <div className="text-slate-500 capitalize">{key.replace(/_/g, ' ')}</div>
                  <div className="font-semibold">
                    {typeof value === 'number'
                      ? formatKeyedNumber(key, value)
                      : String(value)}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : rows.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No data in this period.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    {headers.map((h) => (
                      <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => (
                    <tr key={row.id || idx} className="border-t">
                      {cellsFor(row).map((cell: any, i: number) => (
                        <td
                          key={i}
                          className={`px-3 py-2 ${typeof cell === 'number' ? 'text-right' : ''}`}
                        >
                          {typeof cell === 'number'
                            ? formatKeyedNumber(cellKeys[i] || headers[i], cell)
                            : cell ?? '—'}
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
