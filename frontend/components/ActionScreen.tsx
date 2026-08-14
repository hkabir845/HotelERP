'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoneyCell } from '@/lib/money'
import { getOpsPreset, type Field, type OpsPreset } from '@/lib/ops-presets'

export default function ActionScreen({
  title,
  kind,
  subtitle,
}: {
  title: string
  kind: string
  subtitle?: string
}) {
  const preset = getOpsPreset(kind)
  if (!preset) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen bg-gray-200">
          <Sidebar />
          <main className="ml-64 p-6">Unknown screen: {kind}</main>
        </div>
      </ProtectedRoute>
    )
  }
  return <ActionBody title={title} preset={preset} subtitle={subtitle} />
}

function ActionBody({ title, preset, subtitle }: { title: string; preset: OpsPreset; subtitle?: string }) {
  const [items, setItems] = useState<any[]>([])
  const [form, setForm] = useState<Record<string, string>>({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)
  const endpoint = preset.endpoint || '/ops'

  const load = () => {
    const params = new URLSearchParams({ kind: preset.kind })
    if (preset.pending) params.set('pending', '1')
    apiClient
      .get(`${endpoint}?${params.toString()}`)
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [preset.kind, endpoint])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload: Record<string, any> = { ...form, kind: preset.postKind || preset.kind }
      if (preset.kind === 'hr_punch') payload.action = 'punch_in'
      await apiClient.post(endpoint, payload)
      setForm({})
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const runAction = async (row: any, action: string) => {
    setBusyId(row.id)
    setError('')
    try {
      const path = preset.actionEndpoint
        ? preset.actionEndpoint(row.id)
        : preset.endpoint
          ? `${preset.endpoint}`
          : `/ops/${row.id}/action`
      const body =
        preset.kind === 'hr_punch'
          ? { action, employee_id: row.employee_id || row.id, title: row.title }
          : { action }
      if (preset.kind === 'hr_punch') {
        await apiClient.post('/hr/attendance', body)
      } else {
        await apiClient.post(path, body)
      }
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    } finally {
      setBusyId(null)
    }
  }

  const visibleActions = (row: any) =>
    preset.actions.filter((a) => !a.from || a.from.includes(row.status) || !row.status)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-1 text-gray-600">{subtitle || preset.subtitle}</p>
          {error && <p className="mt-3 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

          <form onSubmit={submit} className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4">
            {preset.fields.map((field) => (
              <FieldInput key={field.key} field={field} form={form} setForm={setForm} />
            ))}
            <div className="flex items-end">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {saving ? 'Saving…' : preset.kind === 'hr_punch' ? 'Punch in' : 'Save'}
              </button>
            </div>
          </form>

          <div className="mt-6 overflow-x-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {preset.columns.map((c) => (
                    <th key={c.key} className="px-4 py-3">
                      {c.label}
                    </th>
                  ))}
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 && (
                  <tr>
                    <td colSpan={preset.columns.length + 1} className="px-4 py-8 text-center text-slate-500">
                      No records yet.
                    </td>
                  </tr>
                )}
                {items.map((row) => (
                  <tr key={row.id} className="border-t">
                    {preset.columns.map((c) => (
                      <td key={c.key} className="px-4 py-3">
                        {c.key === 'status' ? (
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs">{String(row[c.key] ?? '')}</span>
                        ) : (
                          formatMoneyCell(c.key, row[c.key])
                        )}
                      </td>
                    ))}
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {visibleActions(row).map((a) => (
                          <button
                            key={a.id}
                            type="button"
                            disabled={busyId === row.id}
                            onClick={() => runAction(row, a.id)}
                            className="rounded border px-2 py-1 text-xs hover:bg-slate-50 disabled:opacity-50"
                          >
                            {a.label}
                          </button>
                        ))}
                      </div>
                    </td>
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

function FieldInput({
  field,
  form,
  setForm,
}: {
  field: Field
  form: Record<string, string>
  setForm: (fn: (prev: Record<string, string>) => Record<string, string>) => void
}) {
  const span = field.type === 'textarea' ? 'sm:col-span-2 lg:col-span-4' : ''
  return (
    <label className={`text-sm ${span}`}>
      <span className="mb-1 block text-slate-600">{field.label}</span>
      {field.type === 'textarea' ? (
        <textarea
          className="w-full rounded-lg border px-3 py-2"
          rows={2}
          value={form[field.key] || ''}
          onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
        />
      ) : field.type === 'select' ? (
        <select
          className="w-full rounded-lg border px-3 py-2"
          value={form[field.key] || ''}
          onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
        >
          <option value="">Select</option>
          {(field.options || []).map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={field.type || 'text'}
          className="w-full rounded-lg border px-3 py-2"
          value={form[field.key] || ''}
          onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
        />
      )}
    </label>
  )
}
