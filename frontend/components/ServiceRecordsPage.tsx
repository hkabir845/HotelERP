'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoneyCell } from '@/lib/money'

type Field = { key: string; label: string; type?: string }

type Props = {
  title: string
  subtitle: string
  endpoint: string
  extraParams?: Record<string, string>
  createKind?: string
  fields: Field[]
  columns: { key: string; label: string }[]
  readOnly?: boolean
}

export default function ServiceRecordsPage({
  title,
  subtitle,
  endpoint,
  extraParams,
  createKind,
  fields,
  columns,
  readOnly = false,
}: Props) {
  const [items, setItems] = useState<any[]>([])
  const [form, setForm] = useState<Record<string, string>>({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    const qs = extraParams ? '?' + new URLSearchParams(extraParams).toString() : ''
    apiClient
      .get(endpoint + qs)
      .then((res) => {
        const data = res.data || {}
        setItems(data.items || data.reservations || data.purchases || data.sales || [])
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [endpoint])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post(endpoint, { ...form, ...(createKind ? { kind: createKind } : {}), ...extraParams })
      setForm({})
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-1 text-gray-600">{subtitle}</p>
          {error && <p className="mt-3 text-red-600">{error}</p>}

          {!readOnly && (
          <form onSubmit={submit} className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4">
            {fields.map((f) => (
              <label key={f.key} className="text-sm">
                <span className="mb-1 block text-slate-600">{f.label}</span>
                <input
                  type={f.type || 'text'}
                  className="w-full rounded-lg border px-3 py-2"
                  value={form[f.key] || ''}
                  onChange={(e) => setForm((prev) => ({ ...prev, [f.key]: e.target.value }))}
                />
              </label>
            ))}
            <div className="flex items-end">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Add'}
              </button>
            </div>
          </form>
          )}

          <div className="mt-6 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {columns.map((c) => (
                    <th key={c.key} className="px-4 py-3">
                      {c.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                      No records yet.
                    </td>
                  </tr>
                )}
                {items.map((row) => (
                  <tr key={row.id} className="border-t">
                    {columns.map((c) => (
                      <td key={c.key} className="px-4 py-3">
                        {formatMoneyCell(c.key, row[c.key])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
