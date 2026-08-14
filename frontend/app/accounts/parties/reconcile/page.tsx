'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function PartyReconcilePage() {
  const [asOf, setAsOf] = useState(today())
  const [results, setResults] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    apiClient
      .get(`/accounts/parties/reconcile?as_of=${asOf}`)
      .then((res) => setResults(res.data.results || []))
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
          <Link href="/accounts/parties" className="text-sm text-indigo-700">
            Back to party ledgers
          </Link>
          <h1 className="mt-4 text-3xl font-bold text-gray-900">Party ↔ Control reconcile</h1>
          <p className="mt-1 text-gray-600">
            Sum of subsidiary party balances vs the control GL account (AR, AP, loans). Difference should trend to zero as postings stay in sync.
          </p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">As of</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={asOf} onChange={(e) => setAsOf(e.target.value)} />
            </label>
            <button type="button" onClick={load} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
              Run
            </button>
          </div>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : results.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No control accounts with party ledgers yet.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Control</th>
                    <th className="px-3 py-2 text-right">Parties</th>
                    <th className="px-3 py-2 text-right">Party total</th>
                    <th className="px-3 py-2 text-right">GL balance</th>
                    <th className="px-3 py-2 text-right">Difference</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((row) => (
                    <tr key={row.control_account_id} className="border-t">
                      <td className="px-3 py-2">
                        {row.control_code} {row.control_name}
                      </td>
                      <td className="px-3 py-2 text-right">{row.party_count}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.party_total)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.gl_balance)}</td>
                      <td
                        className={`px-3 py-2 text-right tabular-nums font-medium ${
                          Math.abs(row.difference || 0) < 0.005 ? 'text-emerald-700' : 'text-amber-700'
                        }`}
                      >
                        {formatMoney(row.difference)}
                      </td>
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
