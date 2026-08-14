'use client'

import { useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  FRONTDESK_MASTERS,
  ROOM_STATUSES,
  type MasterDef,
  type MasterField,
} from '@/lib/frontdesk-config'
import { Pencil, Plus, RefreshCw, Search, Trash2, X } from 'lucide-react'

type Options = Record<string, { id: number | string; name: string }[]>

function emptyForm(fields: MasterField[]) {
  const form: Record<string, string | boolean> = {}
  for (const field of fields) {
    form[field.key] = field.type === 'checkbox' ? field.key === 'is_active' || field.key === 'is_available' : ''
  }
  return form
}

function display(value: unknown) {
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (value === null || value === undefined || value === '') return '—'
  return String(value)
}

export default function ConfigMasterPage({
  kind,
  catalog,
  endpoint = '/frontdesk/config',
  queryParams,
  defaults,
  titleOverride,
  subtitleOverride,
}: {
  kind: string
  catalog?: Record<string, MasterDef>
  endpoint?: string
  queryParams?: Record<string, string>
  defaults?: Record<string, string | boolean>
  titleOverride?: string
  subtitleOverride?: string
}) {
  const def = (catalog || FRONTDESK_MASTERS)[kind]
  const [items, setItems] = useState<any[]>([])
  const [options, setOptions] = useState<Options>({})
  const [form, setForm] = useState<Record<string, string | boolean>>({})
  const [editingId, setEditingId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  const mergedOptions = useMemo(
    () => ({ ...options, room_statuses: ROOM_STATUSES }),
    [options]
  )

  const withDefaults = (base: Record<string, string | boolean>) => ({
    ...base,
    ...(defaults || {}),
  })

  const load = (term = search) => {
    const params = new URLSearchParams()
    if (term) params.set('search', term)
    if (queryParams) {
      Object.entries(queryParams).forEach(([key, value]) => {
        if (value) params.set(key, value)
      })
    }
    const qs = params.toString()
    return apiClient
      .get(`${endpoint}/${kind}${qs ? `?${qs}` : ''}`)
      .then((res) => {
        setItems(res.data.items || [])
        setOptions(res.data.options || {})
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!def) return
    setForm(withDefaults(emptyForm(def.fields)))
    setLoading(true)
    load('')
  }, [kind, endpoint, JSON.stringify(queryParams || {}), JSON.stringify(defaults || {})])

  useEffect(() => {
    if (!def) return
    const timer = setTimeout(() => load(search), 250)
    return () => clearTimeout(timer)
  }, [search])

  if (!def) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen bg-gray-200">
          <Sidebar />
          <main className="ml-64 p-6">Unknown config: {kind}</main>
        </div>
      </ProtectedRoute>
    )
  }

  const reset = () => {
    setEditingId(null)
    setForm(withDefaults(emptyForm(def.fields)))
    setError('')
  }

  const editRow = (row: any) => {
    const next = emptyForm(def.fields)
    for (const field of def.fields) {
      const value = row[field.key]
      if (field.type === 'checkbox') next[field.key] = Boolean(value)
      else next[field.key] = value === null || value === undefined ? '' : String(value)
    }
    setForm(withDefaults(next))
    setEditingId(row.id)
    setError('')
  }

  const payload = () => {
    const body: Record<string, any> = { ...(defaults || {}) }
    for (const field of def.fields) {
      const value = form[field.key]
      if (field.type === 'checkbox') body[field.key] = Boolean(value)
      else if (value === '') body[field.key] = field.type === 'select' ? null : ''
      else body[field.key] = value
    }
    return body
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingId) {
        await apiClient.patch(`${endpoint}/${kind}/${editingId}`, payload())
      } else {
        await apiClient.post(`${endpoint}/${kind}`, payload())
      }
      reset()
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: number) => {
    if (!confirm('Delete this record?')) return
    setError('')
    try {
      await apiClient.delete(`${endpoint}/${kind}/${id}`)
      if (editingId === id) reset()
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Delete failed')
    }
  }

  const renderField = (field: MasterField) => {
    const value = form[field.key]
    if (field.type === 'checkbox') {
      return (
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            className="h-4 w-4"
            checked={Boolean(value)}
            onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.checked }))}
          />
          {field.label}
        </label>
      )
    }
    if (field.type === 'select') {
      const opts = mergedOptions[field.optionsKey || ''] || []
              const valKey = field.optionValue || 'id'
              return (
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">
                    {field.label}
                    {field.required ? ' *' : ''}
                  </span>
                  <select
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    value={String(value ?? '')}
                    onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                    required={field.required}
                  >
                    <option value="">Select…</option>
                    {opts.map((opt) => {
                      const optValue = valKey === 'name' ? opt.name : String(opt.id)
                      return (
                        <option key={String(opt.id)} value={optValue}>
                          {opt.name}
                        </option>
                      )
                    })}
                  </select>
                </label>
              )
    }
    if (field.type === 'textarea') {
      return (
        <label className="text-sm sm:col-span-2">
          <span className="mb-1 block text-slate-600">{field.label}</span>
          <textarea
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
            rows={2}
            value={String(value ?? '')}
            onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
          />
        </label>
      )
    }
    return (
      <label className="text-sm">
        <span className="mb-1 block text-slate-600">
          {field.label}
          {field.required ? ' *' : ''}
        </span>
        <input
          type={field.type || 'text'}
          className="w-full rounded-lg border border-gray-300 px-3 py-2"
          value={String(value ?? '')}
          required={field.required}
          placeholder={field.placeholder}
          onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
        />
      </label>
    )
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{titleOverride || def.title}</h1>
              <p className="mt-1 text-gray-600">{subtitleOverride || def.subtitle}</p>
            </div>
            <button
              type="button"
              onClick={() => load()}
              className="rounded-lg border border-gray-300 bg-white p-2 text-gray-600 hover:bg-gray-100"
            >
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>

          {error && <p className="mb-4 text-red-600">{error}</p>}

          <form
            onSubmit={submit}
            className="mb-6 grid gap-3 rounded-xl border border-gray-200 bg-white p-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            {def.fields.map((field) => (
              <div key={field.key}>{renderField(field)}</div>
            ))}
            <div className="flex items-end gap-2">
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {editingId ? <Pencil className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                {saving ? 'Saving…' : editingId ? 'Update' : 'Add'}
              </button>
              {editingId && (
                <button
                  type="button"
                  onClick={reset}
                  className="inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm"
                >
                  <X className="h-4 w-4" />
                  Cancel
                </button>
              )}
            </div>
          </form>

          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm"
              placeholder="Search…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {def.columns.map((col) => (
                    <th key={col.key} className="px-4 py-3 font-medium">
                      {col.label}
                    </th>
                  ))}
                  <th className="px-4 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={def.columns.length + 1} className="px-4 py-10 text-center text-slate-500">
                      Loading…
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={def.columns.length + 1} className="px-4 py-10 text-center text-slate-500">
                      No records yet. Add the first {def.title.toLowerCase()}.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t hover:bg-slate-50">
                      {def.columns.map((col) => (
                        <td key={col.key} className="px-4 py-3">
                          {display(row[col.key])}
                        </td>
                      ))}
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => editRow(row)}
                            className="rounded border px-2 py-1 text-indigo-700 hover:bg-indigo-50"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => remove(row.id)}
                            className="rounded border px-2 py-1 text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
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
