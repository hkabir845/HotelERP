'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

const TYPES = [
  { value: 'asset', label: 'Asset' },
  { value: 'liability', label: 'Liability' },
  { value: 'equity', label: 'Equity' },
  { value: 'revenue', label: 'Revenue' },
  { value: 'expense', label: 'Expense' },
]

function today() {
  return new Date().toISOString().slice(0, 10)
}

type Account = {
  id: number
  code: string
  name: string
  account_type: string
  parent_id: number | null
  opening_balance: number
  opening_balance_as_of: string | null
  opening_balance_journal_id: number | null
  balance: number
  is_group: boolean
  book: string
  is_active: boolean
}

export default function AccountMasterPage({ asGroup }: { asGroup: boolean }) {
  const [items, setItems] = useState<Account[]>([])
  const [groups, setGroups] = useState<Account[]>([])
  const [form, setForm] = useState({
    code: '',
    name: '',
    account_type: asGroup ? 'asset' : 'expense',
    parent_id: '',
    opening_balance: '0',
    opening_balance_as_of: today(),
    book: '',
    description: '',
    is_active: true,
  })
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    apiClient
      .get('/accounts/chart-of-accounts')
      .then((res) => {
        const flat: Account[] = res.data.flat || []
        setItems(flat.filter((row) => row.is_group === asGroup))
        setGroups(flat.filter((row) => row.is_group))
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [asGroup])

  const reset = () => {
    setEditingId(null)
    setForm({
      code: '',
      name: '',
      account_type: asGroup ? 'asset' : 'expense',
      parent_id: '',
      opening_balance: '0',
      opening_balance_as_of: today(),
      book: '',
      description: '',
      is_active: true,
    })
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    const opening = asGroup ? 0 : Number(form.opening_balance || 0)
    const body = {
      code: form.code,
      name: form.name,
      account_type: form.account_type,
      parent_id: form.parent_id || null,
      opening_balance: opening,
      opening_balance_as_of: asGroup || !opening ? null : form.opening_balance_as_of || today(),
      book: asGroup ? '' : form.book,
      description: form.description,
      is_group: asGroup,
      is_active: form.is_active,
    }
    try {
      if (editingId) await apiClient.patch(`/accounts/chart-of-accounts/${editingId}`, body)
      else await apiClient.post('/accounts/chart-of-accounts', body)
      reset()
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
          <h1 className="text-3xl font-bold text-gray-900">{asGroup ? 'Account Group' : 'Account'}</h1>
          <p className="mt-1 text-gray-600">
            {asGroup
              ? 'Groups hold posting accounts. Vouchers cannot post to a group.'
              : 'Posting accounts used on vouchers. Opening balance posts a journal vs Opening Balance Equity as of the date you set.'}
          </p>
          {error && <p className="mt-4 text-red-600">{error}</p>}

          <form onSubmit={submit} className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Code *</span>
              <input className="w-full rounded-lg border px-3 py-2" value={form.code} required onChange={(e) => setForm({ ...form, code: e.target.value })} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Name *</span>
              <input className="w-full rounded-lg border px-3 py-2" value={form.name} required onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Type</span>
              <select className="w-full rounded-lg border px-3 py-2" value={form.account_type} onChange={(e) => setForm({ ...form, account_type: e.target.value })}>
                {TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Parent group</span>
              <select className="w-full rounded-lg border px-3 py-2" value={form.parent_id} onChange={(e) => setForm({ ...form, parent_id: e.target.value })}>
                <option value="">None</option>
                {groups
                  .filter((g) => g.id !== editingId)
                  .map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.code} {g.name}
                    </option>
                  ))}
              </select>
            </label>
            {!asGroup && (
              <>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Opening balance</span>
                  <input
                    type="number"
                    step="0.01"
                    className="w-full rounded-lg border px-3 py-2"
                    value={form.opening_balance}
                    onChange={(e) => setForm({ ...form, opening_balance: e.target.value })}
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Opening as of</span>
                  <input
                    type="date"
                    className="w-full rounded-lg border px-3 py-2"
                    value={form.opening_balance_as_of}
                    onChange={(e) => setForm({ ...form, opening_balance_as_of: e.target.value })}
                    disabled={Number(form.opening_balance || 0) === 0}
                  />
                  <span className="mt-1 block text-xs text-slate-500">Journal date for the opening posting (vs equity 3200).</span>
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Cash / Bank book</span>
                  <select className="w-full rounded-lg border px-3 py-2" value={form.book} onChange={(e) => setForm({ ...form, book: e.target.value })}>
                    <option value="">Neither</option>
                    <option value="cash">Cash</option>
                    <option value="bank">Bank</option>
                  </select>
                </label>
              </>
            )}
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Description</span>
              <input className="w-full rounded-lg border px-3 py-2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              Active
            </label>
            <div className="flex items-end gap-2">
              <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50">
                {saving ? 'Saving…' : editingId ? 'Update' : 'Add'}
              </button>
              {editingId && (
                <button type="button" onClick={reset} className="rounded-lg border px-3 py-2 text-sm">
                  Cancel
                </button>
              )}
            </div>
          </form>

          <div className="mt-6 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3">Code</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Type</th>
                  {!asGroup && <th className="px-4 py-3">Book</th>}
                  {!asGroup && <th className="px-4 py-3 text-right">Opening</th>}
                  {!asGroup && <th className="px-4 py-3">As of</th>}
                  {!asGroup && <th className="px-4 py-3">Journal</th>}
                  {!asGroup && <th className="px-4 py-3 text-right">Balance</th>}
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={asGroup ? 4 : 9} className="px-4 py-8 text-center text-slate-500">
                      No records yet.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-4 py-3">{row.code}</td>
                      <td className="px-4 py-3">{row.name}</td>
                      <td className="px-4 py-3 capitalize">{row.account_type}</td>
                      {!asGroup && <td className="px-4 py-3">{row.book || '—'}</td>}
                      {!asGroup && <td className="px-4 py-3 text-right">{formatMoney(row.opening_balance || 0)}</td>}
                      {!asGroup && <td className="px-4 py-3">{row.opening_balance_as_of || '—'}</td>}
                      {!asGroup && (
                        <td className="px-4 py-3">
                          {row.opening_balance_journal_id ? (
                            <Link href={`/accounts/vouchers/${row.opening_balance_journal_id}`} className="text-indigo-700 hover:underline">
                              View
                            </Link>
                          ) : (
                            '—'
                          )}
                        </td>
                      )}
                      {!asGroup && <td className="px-4 py-3 text-right">{formatMoney(row.balance || 0)}</td>}
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          className="text-indigo-700"
                          onClick={() => {
                            setEditingId(row.id)
                            setForm({
                              code: row.code,
                              name: row.name,
                              account_type: row.account_type,
                              parent_id: row.parent_id ? String(row.parent_id) : '',
                              opening_balance: String(row.opening_balance || 0),
                              opening_balance_as_of: row.opening_balance_as_of || today(),
                              book: row.book || '',
                              description: '',
                              is_active: row.is_active,
                            })
                          }}
                        >
                          Edit
                        </button>
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
