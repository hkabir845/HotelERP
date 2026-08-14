'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import CoaAccountSelect from '@/components/CoaAccountSelect'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import { ArrowDownCircle, Search, RefreshCw, AlertCircle, Plus } from 'lucide-react'
import { formatMoney } from '@/lib/money'
import { COA, leafAccounts, suggestedExpenseAccountId, type CoaPick } from '@/lib/coaDefaults'
import { mergeSuggestedStringField } from '@/lib/coaSuggestForm'

interface Payable {
  id: number
  invoice_number: string
  vendor_name: string
  invoice_date: string
  due_date: string
  total_amount: number
  paid_amount: number
  balance: number
  status: string
  days_overdue: number
}

export default function AccountsPayablePage() {
  const router = useRouter()
  const [payables, setPayables] = useState<Payable[]>([])
  const [accounts, setAccounts] = useState<CoaPick[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showForm, setShowForm] = useState(false)
  const [expenseTouched, setExpenseTouched] = useState(false)
  const [form, setForm] = useState({
    vendor_name: '',
    invoice_number: '',
    invoice_date: new Date().toISOString().slice(0, 10),
    due_date: new Date().toISOString().slice(0, 10),
    amount: '',
    expense_account_id: '',
    notes: '',
  })

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    partial: { label: 'Partial', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    paid: { label: 'Paid', color: 'text-green-700', bgColor: 'bg-green-100' },
    overdue: { label: 'Overdue', color: 'text-red-700', bgColor: 'bg-red-100' },
  }

  const fetchPayables = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchTerm) params.append('search', searchTerm)
      const response = await apiClient.get(`/accounts/payable?${params.toString()}`)
      setPayables(response.data.payables || [])
      const coa = await apiClient.get('/accounts/chart-of-accounts')
      const picks = leafAccounts(coa.data.flat || [])
      setAccounts(picks.filter((a) => !a.account_type || a.account_type === 'expense'))
      const suggested = suggestedExpenseAccountId(picks, 'purchases')
      setForm((prev) => ({
        ...prev,
        expense_account_id: mergeSuggestedStringField(prev.expense_account_id, suggested, expenseTouched),
      }))
    } catch (err) {
      console.error(err)
      setPayables([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPayables()
  }, [statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchPayables(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/accounts/payable', {
        ...form,
        amount: Number(form.amount),
        expense_account_id: form.expense_account_id ? Number(form.expense_account_id) : undefined,
      })
      setShowForm(false)
      setExpenseTouched(false)
      setForm({
        vendor_name: '',
        invoice_number: '',
        invoice_date: new Date().toISOString().slice(0, 10),
        due_date: new Date().toISOString().slice(0, 10),
        amount: '',
        expense_account_id: suggestedExpenseAccountId(accounts, 'purchases'),
        notes: '',
      })
      await fetchPayables()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create bill')
    } finally {
      setSaving(false)
    }
  }

  const totalPayable = payables.reduce((sum, p) => sum + p.balance, 0)
  const overdueCount = payables.filter((p) => p.status === 'overdue').length
  const overdueAmount = payables.filter((p) => p.status === 'overdue').reduce((sum, p) => sum + p.balance, 0)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <ArrowDownCircle className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Accounts Payable</h1>
                  <p className="text-gray-600 mt-1">Vendor bills post to Purchases / AP (editable account)</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowForm((v) => !v)}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
                >
                  <Plus className="h-4 w-4" /> New bill
                </button>
                <button onClick={fetchPayables} className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg">
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>
            </div>

            {error && <p className="mb-4 text-red-600">{error}</p>}

            {showForm && (
              <form onSubmit={submit} className="mb-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-3">
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Vendor *</span>
                  <input required className="w-full rounded-lg border px-3 py-2" value={form.vendor_name} onChange={(e) => setForm({ ...form, vendor_name: e.target.value })} />
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
                  label="Expense account"
                  hint="Auto-suggested: Purchases / Food Cost (5300). Change for rent, utilities, etc."
                  value={form.expense_account_id}
                  accounts={accounts}
                  recommendedCode={COA.PURCHASES}
                  onChange={(v) => {
                    setExpenseTouched(!!v)
                    setForm({ ...form, expense_account_id: v })
                  }}
                  filter={(a) => !a.account_type || a.account_type === 'expense' || String(a.account_name || a.name || '').length > 0}
                />
                <label className="text-sm sm:col-span-2">
                  <span className="mb-1 block text-slate-600">Notes</span>
                  <input className="w-full rounded-lg border px-3 py-2" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                </label>
                <div className="flex items-end">
                  <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">
                    {saving ? 'Saving…' : 'Create & post to GL'}
                  </button>
                </div>
              </form>
            )}

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg border p-4">
                <div className="text-sm text-gray-600">Total Payable</div>
                <div className="text-2xl font-bold mt-1">{formatMoney(totalPayable)}</div>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="text-sm text-gray-600">Overdue</div>
                <div className="text-2xl font-bold text-red-600 mt-1">{overdueCount}</div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="text-sm text-gray-600">Overdue Amount</div>
                <div className="text-2xl font-bold text-orange-600 mt-1">{formatMoney(overdueAmount)}</div>
              </div>
              <div className="bg-white rounded-lg border p-4">
                <div className="text-sm text-gray-600">Total Invoices</div>
                <div className="text-2xl font-bold mt-1">{payables.length}</div>
              </div>
            </div>

            {overdueCount > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="font-medium text-red-900">{overdueCount} invoice(s) overdue</span>
              </div>
            )}

            <div className="bg-white rounded-lg border p-4 mb-6">
              <div className="flex flex-wrap gap-4">
                <div className="relative flex-1 min-w-[200px]">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    placeholder="Search invoice #, vendor…"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-lg"
                  />
                </div>
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-4 py-2 border rounded-lg">
                  <option value="all">All Statuses</option>
                  {Object.entries(statusConfig).map(([value, config]) => (
                    <option key={value} value={value}>{config.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {loading ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-600" />
              </div>
            ) : payables.length === 0 ? (
              <div className="bg-white rounded-lg border p-12 text-center text-gray-600">No payables yet — create a vendor bill above.</div>
            ) : (
              <div className="bg-white rounded-lg border overflow-hidden">
                <table className="min-w-full divide-y">
                  <thead className="bg-gray-100 text-left text-xs uppercase text-gray-500">
                    <tr>
                      <th className="px-4 py-3">Invoice</th>
                      <th className="px-4 py-3">Vendor</th>
                      <th className="px-4 py-3">Due</th>
                      <th className="px-4 py-3">Total</th>
                      <th className="px-4 py-3">Balance</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {payables.map((p) => {
                      const st = statusConfig[p.status] || statusConfig.pending
                      return (
                        <tr key={p.id}>
                          <td className="px-4 py-3 text-sm font-medium">{p.invoice_number}</td>
                          <td className="px-4 py-3 text-sm">{p.vendor_name}</td>
                          <td className="px-4 py-3 text-sm">{p.due_date}</td>
                          <td className="px-4 py-3 text-sm">{formatMoney(p.total_amount)}</td>
                          <td className="px-4 py-3 text-sm">{formatMoney(p.balance)}</td>
                          <td className="px-4 py-3">
                            <span className={`rounded-full px-2 py-0.5 text-xs ${st.bgColor} ${st.color}`}>{st.label}</span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button type="button" className="text-sm text-indigo-700" onClick={() => router.push('/accounts/payable/payments')}>
                              Pay
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
