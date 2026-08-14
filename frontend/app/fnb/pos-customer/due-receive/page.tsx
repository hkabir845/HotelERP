'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { Plus, RefreshCw, Search } from 'lucide-react'

type Row = {
  id: number
  customer_name: string
  receive_date: string
  amount: number
  method: string
  notes: string
  created_by: string
}

export default function Page() {
  const [items, setItems] = useState<Row[]>([])
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = (term = search) => {
    const params = new URLSearchParams()
    if (term) params.set('search', term)
    const qs = params.toString()
    setLoading(true)
    apiClient
      .get(`/fnb/config/due-receives${qs ? `?${qs}` : ''}`)
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load('')
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => load(search), 250)
    return () => clearTimeout(timer)
  }, [search])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Due Receive</h1>
              <p className="mt-1 text-gray-600">Payments collected against POS customer outstanding.</p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => load()}
                className="rounded-lg border border-gray-300 bg-white p-2 text-gray-600 hover:bg-gray-100"
              >
                <RefreshCw className="h-5 w-5" />
              </button>
              <Link
                href="/fnb/pos-customer/due-receive/new"
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
              >
                <Plus className="h-4 w-4" />
                Receive
              </Link>
            </div>
          </div>

          {error && <p className="mb-4 text-red-600">{error}</p>}

          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm"
              placeholder="Search customer…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Date</th>
                  <th className="px-4 py-3 font-medium">Customer</th>
                  <th className="px-4 py-3 font-medium">Method</th>
                  <th className="px-4 py-3 font-medium text-right">Amount</th>
                  <th className="px-4 py-3 font-medium">Notes</th>
                  <th className="px-4 py-3 font-medium">Received by</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-slate-500">
                      Loading…
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-slate-500">
                      No due receives yet.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-4 py-3">{row.receive_date}</td>
                      <td className="px-4 py-3">{row.customer_name}</td>
                      <td className="px-4 py-3 capitalize">{row.method}</td>
                      <td className="px-4 py-3 text-right">
                        {Number(row.amount).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-4 py-3">{row.notes || '—'}</td>
                      <td className="px-4 py-3">{row.created_by || '—'}</td>
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
