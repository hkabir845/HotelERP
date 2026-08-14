'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Plus, RefreshCw } from 'lucide-react'

type Column = { key: string; label: string }

export default function InventoryDocList({
  title,
  subtitle,
  endpoint,
  createPath,
  createLabel = 'Add new',
  columns,
  query,
  postAction = 'post',
}: {
  title: string
  subtitle: string
  endpoint: string
  createPath?: string
  createLabel?: string
  columns: Column[]
  query?: string
  postAction?: string
}) {
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get(`${endpoint}${query || ''}`)
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [endpoint, query])

  const act = async (id: number, action: string) => {
    setError('')
    try {
      await apiClient.post(`${endpoint}/${id}`, { action })
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    }
  }

  const money = (n: any) =>
    n === null || n === undefined || n === ''
      ? '—'
      : formatMoney(n)

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
              <button
                type="button"
                onClick={load}
                className="rounded-lg border bg-white p-2 text-gray-600"
              >
                <RefreshCw className="h-5 w-5" />
              </button>
              {createPath && (
                <Link
                  href={createPath}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
                >
                  <Plus className="h-4 w-4" />
                  {createLabel}
                </Link>
              )}
            </div>
          </div>
          {error && <p className="mb-4 text-red-600">{error}</p>}
          <div className="overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {columns.map((col) => (
                    <th key={col.key} className="px-3 py-2 font-medium whitespace-nowrap">
                      {col.label}
                    </th>
                  ))}
                  <th className="px-3 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={columns.length + 1} className="px-4 py-10 text-center text-slate-500">
                      Loading…
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length + 1} className="px-4 py-10 text-center text-slate-500">
                      No records yet.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t">
                      {columns.map((col) => {
                        const value = row[col.key]
                        const isNum = ['total_amount', 'amount', 'total_cost', 'due', 'paid_amount'].includes(col.key)
                        return (
                          <td key={col.key} className={`px-3 py-2 ${isNum ? 'text-right' : ''}`}>
                            {typeof value === 'boolean'
                              ? value
                                ? 'Yes'
                                : 'No'
                              : isNum
                                ? money(value)
                                : value ?? '—'}
                          </td>
                        )
                      })}
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {row.status === 'pending' && endpoint.includes('requisition') && (
                            <>
                              <button
                                type="button"
                                onClick={() => act(row.id, 'approve')}
                                className="rounded border px-2 py-1 text-indigo-700"
                              >
                                Approve
                              </button>
                              <button
                                type="button"
                                onClick={() => act(row.id, 'reject')}
                                className="rounded border px-2 py-1 text-red-700"
                              >
                                Reject
                              </button>
                            </>
                          )}
                          {row.can_post && (
                            <button
                              type="button"
                              onClick={() => act(row.id, postAction)}
                              className="rounded border px-2 py-1 text-emerald-700"
                            >
                              {postAction === 'fulfill' ? 'Fulfill' : 'Post'}
                            </button>
                          )}
                        </div>
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
