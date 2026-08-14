'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatKeyedNumber } from '@/lib/money'

type Opt = { id: number; name: string }

function monthStart() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function Page() {
  const [suppliers, setSuppliers] = useState<Opt[]>([])
  const [supplierId, setSupplierId] = useState('')
  const [from, setFrom] = useState(monthStart())
  const [to, setTo] = useState(today())
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<any[]>([])
  const [summary, setSummary] = useState<Record<string, any>>({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    apiClient
      .get('/inventory/config/suppliers')
      .then((res) => setSuppliers(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load suppliers'))
  }, [])

  const load = () => {
    if (!supplierId) {
      setError('Select a supplier')
      return
    }
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ supplier_id: supplierId, from, to })
    apiClient
      .get(`/inventory/suppliers/statement?${params.toString()}`)
      .then((res) => {
        setColumns(res.data.columns || [])
        setRows(res.data.rows || [])
        setSummary(res.data.summary || {})
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  const cellKeys = rows[0] ? Object.keys(rows[0]) : []

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Supplier Statement</h1>
          <p className="mt-1 text-gray-600">Purchases, returns, and payments with running balance.</p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Supplier</span>
              <select
                className="min-w-[220px] rounded-lg border px-3 py-2"
                value={supplierId}
                onChange={(e) => setSupplierId(e.target.value)}
              >
                <option value="">Select…</option>
                {suppliers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">From</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={from} onChange={(e) => setFrom(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">To</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={to} onChange={(e) => setTo(e.target.value)} />
            </label>
            <button type="button" onClick={load} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
              Run
            </button>
          </div>

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
              <p className="p-8 text-center text-slate-500">Select a supplier and run the statement.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    {(columns.length ? columns : cellKeys).map((h) => (
                      <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => (
                    <tr key={idx} className="border-t">
                      {cellKeys.map((k) => (
                        <td key={k} className={`px-3 py-2 ${typeof row[k] === 'number' ? 'text-right' : ''}`}>
                          {typeof row[k] === 'number'
                            ? formatKeyedNumber(k, row[k])
                            : row[k] ?? '—'}
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
