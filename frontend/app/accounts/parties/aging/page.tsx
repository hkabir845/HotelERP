'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function PartyAgingPage() {
  const router = useRouter()
  const [asOf, setAsOf] = useState(today())
  const [partyType, setPartyType] = useState('')
  const [rows, setRows] = useState<any[]>([])
  const [totals, setTotals] = useState<Record<string, number>>({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams({ as_of: asOf })
    if (partyType) params.set('party_type', partyType)
    apiClient
      .get(`/accounts/parties/aging?${params.toString()}`)
      .then((res) => {
        setRows(res.data.rows || [])
        setTotals(res.data.totals || {})
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
          <Link href="/accounts/parties" className="text-sm text-indigo-700">
            Back to party ledgers
          </Link>
          <h1 className="mt-4 text-3xl font-bold text-gray-900">Party Aging</h1>
          <p className="mt-1 text-gray-600">Open AR invoices and AP bills by due-date bucket, linked to party accounts.</p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">As of</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={asOf} onChange={(e) => setAsOf(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Type</span>
              <select className="rounded-lg border px-3 py-2" value={partyType} onChange={(e) => setPartyType(e.target.value)}>
                <option value="">AR + AP</option>
                <option value="customer">Customers</option>
                <option value="guest">Guests</option>
                <option value="vendor">Vendors</option>
                <option value="supplier">Suppliers</option>
              </select>
            </label>
            <button type="button" onClick={load} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
              Run
            </button>
          </div>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : rows.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No open balances.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Code</th>
                    <th className="px-3 py-2">Name</th>
                    <th className="px-3 py-2">Type</th>
                    <th className="px-3 py-2 text-right">Current</th>
                    <th className="px-3 py-2 text-right">1–30</th>
                    <th className="px-3 py-2 text-right">31–60</th>
                    <th className="px-3 py-2 text-right">61–90</th>
                    <th className="px-3 py-2 text-right">90+</th>
                    <th className="px-3 py-2 text-right">Total</th>
                    <th className="px-3 py-2 text-right">Ledger</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr
                      key={row.party_account_id}
                      className="cursor-pointer border-t hover:bg-indigo-50/60"
                      onClick={() => router.push(`/accounts/parties/${row.party_account_id}`)}
                    >
                      <td className="px-3 py-2 text-indigo-700">{row.code}</td>
                      <td className="px-3 py-2">{row.name}</td>
                      <td className="px-3 py-2 capitalize">{row.party_type?.replace('_', ' ')}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.current)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.days_1_30)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.days_31_60)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.days_61_90)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.days_90_plus)}</td>
                      <td className="px-3 py-2 text-right tabular-nums font-medium">{formatMoney(row.total)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.ledger_balance)}</td>
                    </tr>
                  ))}
                  <tr className="border-t bg-slate-50 font-semibold">
                    <td className="px-3 py-2" colSpan={3}>
                      Total
                    </td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.current || 0)}</td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.days_1_30 || 0)}</td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.days_31_60 || 0)}</td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.days_61_90 || 0)}</td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.days_90_plus || 0)}</td>
                    <td className="px-3 py-2 text-right">{formatMoney(totals.total || 0)}</td>
                    <td className="px-3 py-2" />
                  </tr>
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
