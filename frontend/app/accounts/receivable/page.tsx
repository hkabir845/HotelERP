'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import CoaAccountSelect from '@/components/CoaAccountSelect'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import { ArrowUpCircle, Search, RefreshCw, Plus } from 'lucide-react'
import { formatMoney } from '@/lib/money'
import { COA, leafAccounts, suggestedIncomeAccountId, type CoaPick } from '@/lib/coaDefaults'
import { mergeSuggestedStringField } from '@/lib/coaSuggestForm'

interface Receivable {
  id: number
  invoice_number: string
  customer_name: string
  invoice_date: string
  due_date: string
  total_amount: number
  paid_amount: number
  balance: number
  status: string
}

export default function AccountsReceivablePage() {
  const router = useRouter()
  const [rows, setRows] = useState<Receivable[]>([])
  const [accounts, setAccounts] = useState<CoaPick[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [revTouched, setRevTouched] = useState(false)
  const [form, setForm] = useState({
    customer_name: '',
    invoice_number: '',
    invoice_date: new Date().toISOString().slice(0, 10),
    due_date: new Date().toISOString().slice(0, 10),
    amount: '',
    revenue_account_id: '',
    notes: '',
  })

  const load = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      const response = await apiClient.get(`/accounts/receivable?${params}`)
      setRows(response.data.receivables || [])
      const coa = await apiClient.get('/accounts/chart-of-accounts')
      const picks = leafAccounts(coa.data.flat || [])
      setAccounts(picks.filter((a) => !a.account_type || a.account_type === 'revenue'))
      const suggested = suggestedIncomeAccountId(picks, 'room')
      setForm((prev) => ({
        ...prev,
        revenue_account_id: mergeSuggestedStringField(prev.revenue_account_id, suggested, revTouched),
      }))
    } catch {
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    const t = setTimeout(load, 300)
    return () => clearTimeout(t)
  }, [searchTerm])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/accounts/receivable', {
        ...form,
        amount: Number(form.amount),
        revenue_account_id: form.revenue_account_id ? Number(form.revenue_account_id) : undefined,
      })
      setShowForm(false)
      setRevTouched(false)
      setForm({
        customer_name: '',
        invoice_number: '',
        invoice_date: new Date().toISOString().slice(0, 10),
        due_date: new Date().toISOString().slice(0, 10),
        amount: '',
        revenue_account_id: suggestedIncomeAccountId(accounts, 'room'),
        notes: '',
      })
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create invoice')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2">
                <ArrowUpCircle className="h-6 w-6 text-emerald-700" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Accounts Receivable</h1>
                <p className="mt-1 text-gray-600">Customer invoices post to AR / Room revenue (editable)</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button type="button" onClick={() => setShowForm((v) => !v)} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white">
                <Plus className="h-4 w-4" /> New invoice
              </button>
              <button type="button" onClick={load} className="rounded-lg border bg-white p-2">
                <RefreshCw className="h-5 w-5" />
              </button>
            </div>
          </div>

          {error && <p className="mb-4 text-red-600">{error}</p>}

          {showForm && (
            <form onSubmit={submit} className="mb-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-3">
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Customer *</span>
                <input required className="w-full rounded-lg border px-3 py-2" value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Invoice #</span>
                <input className="w-full rounded-lg border px-3 py-2" value={form.invoice_number} onChange={(e) => setForm({ ...form, invoice_number: e.target.value })} />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Amount *</span>
                <input required type="number" min="0.01" step="0.01" className="w-full rounded-lg border px-3 py-2" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Invoice date</span>
                <input type="date" className="w-full rounded-lg border px-3 py-2" value={form.invoice_date} onChange={(e) => setForm({ ...form, invoice_date: e.target.value })} />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Due date</span>
                <input type="date" className="w-full rounded-lg border px-3 py-2" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
              </label>
              <CoaAccountSelect
                label="Revenue account"
                hint="Auto-suggested: Room Revenue (4100). Switch to F&B / Banquet / Other as needed."
                value={form.revenue_account_id}
                accounts={accounts}
                recommendedCode={COA.ROOM_REV}
                onChange={(v) => {
                  setRevTouched(!!v)
                  setForm({ ...form, revenue_account_id: v })
                }}
              />
              <label className="text-sm sm:col-span-2">
                <span className="mb-1 block text-slate-600">Notes</span>
                <input className="w-full rounded-lg border px-3 py-2" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
              </label>
              <div className="flex items-end">
                <button type="submit" disabled={saving} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white disabled:opacity-50">
                  {saving ? 'Saving…' : 'Create & post to GL'}
                </button>
              </div>
            </form>
          )}

          <div className="mb-6 rounded-lg border bg-white p-4">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                className="w-full rounded-lg border py-2 pl-10 pr-4"
                placeholder="Search customer / invoice…"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-emerald-600" />
            </div>
          ) : (
            <div className="overflow-hidden rounded-lg border bg-white">
              <table className="min-w-full divide-y text-sm">
                <thead className="bg-gray-100 text-left text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Invoice</th>
                    <th className="px-4 py-3">Customer</th>
                    <th className="px-4 py-3">Due</th>
                    <th className="px-4 py-3">Total</th>
                    <th className="px-4 py-3">Balance</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {rows.map((r) => (
                    <tr key={r.id}>
                      <td className="px-4 py-3 font-medium">{r.invoice_number}</td>
                      <td className="px-4 py-3">{r.customer_name}</td>
                      <td className="px-4 py-3">{r.due_date}</td>
                      <td className="px-4 py-3">{formatMoney(r.total_amount)}</td>
                      <td className="px-4 py-3">{formatMoney(r.balance)}</td>
                      <td className="px-4 py-3">{r.status}</td>
                      <td className="px-4 py-3 text-right">
                        <button type="button" className="text-emerald-700" onClick={() => router.push('/accounts/receivable/payments')}>
                          Receive
                        </button>
                      </td>
                    </tr>
                  ))}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-4 py-10 text-center text-gray-500">
                        No receivables yet — create a customer invoice above.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
