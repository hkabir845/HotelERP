'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Plus, RefreshCw } from 'lucide-react'
import { coaIdForCode, coaSuffix, templateCoaOptionLabel } from '@/lib/coaDefaults'

type Field = {
  key: string
  label: string
  type?: 'text' | 'number' | 'date' | 'datetime-local' | 'email' | 'textarea' | 'select' | 'checkbox'
  optionsKey?: string
  required?: boolean
  /** Stable COA suffix to auto-select when form field is empty (editable). */
  suggestCode?: string
  /** Show recommended label on empty option using this options list. */
  recommendHint?: boolean
}

type Column = { key: string; label: string }

type Action = { id: string; label: string; flag: string; tone?: 'indigo' | 'emerald' | 'red' }

type Opt = { id: number | string; name: string }

const MONEY = new Set([
  'amount',
  'paid_amount',
  'due',
  'net_pay',
  'gross_pay',
  'expected_value',
  'late_fine',
  'tax',
  'total_deductions',
  'budgeted_amount',
  'actual_amount',
  'variance',
])

function money(n: any) {
  if (n === null || n === undefined || n === '') return '—'
  return formatMoney(n)
}

function emptyForm(fields: Field[]) {
  const form: Record<string, string | boolean> = {}
  for (const field of fields) form[field.key] = field.type === 'checkbox' ? false : ''
  return form
}

export default function RecordWorkbench({
  title,
  subtitle,
  endpoint,
  actionPath,
  fields,
  columns,
  actions = [],
  query = '',
  extraBody = {},
  createLabel = 'Add',
  generateLabel,
  payAction,
}: {
  title: string
  subtitle: string
  endpoint: string
  actionPath?: (id: number) => string
  fields: Field[]
  columns: Column[]
  actions?: Action[]
  query?: string
  extraBody?: Record<string, any>
  createLabel?: string
  generateLabel?: string
  payAction?: string
}) {
  const [items, setItems] = useState<any[]>([])
  const [options, setOptions] = useState<Record<string, Opt[]>>({})
  const [summary, setSummary] = useState<Record<string, any>>({})
  const [form, setForm] = useState<Record<string, string | boolean>>(emptyForm(fields))
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [payId, setPayId] = useState<number | null>(null)
  const [payAmount, setPayAmount] = useState('')
  const [payMethod, setPayMethod] = useState('cash')

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get(`${endpoint}${query}`)
      .then((res) => {
        const nextOptions = res.data.options || {}
        setItems(res.data.items || [])
        setOptions(nextOptions)
        setSummary(res.data.summary || {})
        // Prefill recommended COA fields when empty (user can still change).
        setForm((prev) => {
          const next = { ...prev }
          for (const field of fields) {
            if (!field.suggestCode || field.type !== 'select') continue
            if (String(next[field.key] || '').trim()) continue
            const opts = nextOptions[field.optionsKey || ''] || []
            const picks = opts.map((o: Opt) => ({
              id: Number(o.id),
              account_code: String(o.name || '').split(' ')[0] || '',
              account_name: String(o.name || ''),
            }))
            // Prefer exact code match from option name prefix "{code} {name}"
            const byCode = opts.find((o: Opt) => coaSuffix(String(o.name || '').split(/\s+/)[0] || '') === field.suggestCode)
            if (byCode) {
              next[field.key] = String(byCode.id)
              continue
            }
            const id = coaIdForCode(field.suggestCode, picks)
            if (id) next[field.key] = id
          }
          return next
        })
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    setForm(emptyForm(fields))
    load()
  }, [endpoint, query])

  const payload = () => {
    const body: Record<string, any> = {}
    for (const field of fields) {
      const value = form[field.key]
      if (field.type === 'checkbox') body[field.key] = Boolean(value)
      else if (value === '') body[field.key] = field.type === 'select' ? null : ''
      else body[field.key] = value
    }
    return { ...extraBody, ...body }
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post(endpoint, payload())
      setForm(emptyForm(fields))
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const act = async (id: number, action: string, extra?: Record<string, any>) => {
    setError('')
    try {
      const path = actionPath ? actionPath(id) : `${endpoint}/${id}/action`
      await apiClient.post(path, { action, ...extra })
      setPayId(null)
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    }
  }

  const toneClass = (tone?: Action['tone']) =>
    tone === 'red'
      ? 'text-red-700'
      : tone === 'emerald'
        ? 'text-emerald-700'
        : 'text-indigo-700'

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
            <button type="button" onClick={load} className="rounded-lg border bg-white p-2 text-gray-600">
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>

          {error && <p className="mb-4 text-red-600">{error}</p>}

          {fields.length > 0 && (
            <form
              onSubmit={submit}
              className="mb-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4"
            >
              {fields.map((field) => {
                const value = form[field.key]
                if (field.type === 'checkbox') {
                  return (
                    <label key={field.key} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={Boolean(value)}
                        onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.checked }))}
                      />
                      {field.label}
                    </label>
                  )
                }
                if (field.type === 'select') {
                  const opts = options[field.optionsKey || ''] || []
                  const emptyLabel =
                    field.recommendHint && field.suggestCode
                      ? templateCoaOptionLabel(
                          field.suggestCode,
                          opts.map((o) => ({
                            id: Number(o.id),
                            account_code: String(o.name || '').split(/\s+/)[0] || '',
                            account_name: String(o.name || ''),
                          }))
                        )
                      : 'Select…'
                  return (
                    <label key={field.key} className="text-sm">
                      <span className="mb-1 block text-slate-600">
                        {field.label}
                        {field.required ? ' *' : ''}
                      </span>
                      <select
                        className="w-full rounded-lg border px-3 py-2"
                        required={field.required}
                        value={String(value ?? '')}
                        onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                      >
                        <option value="">{emptyLabel}</option>
                        {opts.map((opt) => (
                          <option key={String(opt.id)} value={String(opt.id)}>
                            {opt.name}
                          </option>
                        ))}
                      </select>
                    </label>
                  )
                }
                if (field.type === 'textarea') {
                  return (
                    <label key={field.key} className="text-sm sm:col-span-2">
                      <span className="mb-1 block text-slate-600">{field.label}</span>
                      <textarea
                        className="w-full rounded-lg border px-3 py-2"
                        rows={2}
                        value={String(value ?? '')}
                        onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                      />
                    </label>
                  )
                }
                return (
                  <label key={field.key} className="text-sm">
                    <span className="mb-1 block text-slate-600">
                      {field.label}
                      {field.required ? ' *' : ''}
                    </span>
                    <input
                      type={field.type || 'text'}
                      className="w-full rounded-lg border px-3 py-2"
                      required={field.required}
                      value={String(value ?? '')}
                      onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                    />
                  </label>
                )
              })}
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
                >
                  <Plus className="h-4 w-4" />
                  {saving ? 'Saving…' : generateLabel || createLabel}
                </button>
              </div>
            </form>
          )}

          {summary && Object.keys(summary).length > 0 && (
            <div className="mb-4 flex flex-wrap gap-4 text-sm">
              {Object.entries(summary).map(([key, value]) => (
                <div key={key} className="rounded-lg border bg-white px-4 py-2">
                  <div className="capitalize text-slate-500">{key.replace(/_/g, ' ')}</div>
                  <div className="font-semibold">
                    {typeof value === 'number' && !['slips', 'events', 'invoices', 'staff', 'payments', 'leads'].includes(key)
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
                  {columns.map((col) => (
                    <th key={col.key} className="px-3 py-2 font-medium whitespace-nowrap">
                      {col.label}
                    </th>
                  ))}
                  {actions.length > 0 && <th className="px-3 py-2 font-medium">Actions</th>}
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
                    <tr key={row.id} className="border-t align-top">
                      {columns.map((col) => {
                        const value = row[col.key]
                        const isMoney = MONEY.has(col.key)
                        return (
                          <td key={col.key} className={`px-3 py-2 ${isMoney ? 'text-right' : ''}`}>
                            {typeof value === 'boolean'
                              ? value
                                ? 'Yes'
                                : 'No'
                              : isMoney
                                ? money(value)
                                : value ?? '—'}
                          </td>
                        )
                      })}
                      {actions.length > 0 && (
                        <td className="px-3 py-2">
                          <div className="flex flex-wrap gap-1">
                            {actions.map((action) =>
                              row[action.flag] ? (
                                <button
                                  key={action.id}
                                  type="button"
                                  onClick={() => {
                                    if (payAction && action.id === payAction) {
                                      setPayId(row.id)
                                      setPayAmount(String(row.due || row.net_pay || row.amount || ''))
                                    } else {
                                      act(row.id, action.id)
                                    }
                                  }}
                                  className={`rounded border px-2 py-1 ${toneClass(action.tone)}`}
                                >
                                  {action.label}
                                </button>
                              ) : null
                            )}
                          </div>
                          {payId === row.id && payAction && (
                            <div className="mt-2 flex flex-wrap items-end gap-2">
                              <input
                                type="number"
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
                                  act(row.id, payAction, { amount: Number(payAmount), method: payMethod })
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
                      )}
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
