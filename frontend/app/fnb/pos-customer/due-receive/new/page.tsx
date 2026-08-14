'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

type Customer = { id: number; name: string; due_balance?: number }

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function Page() {
  const router = useRouter()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [customerId, setCustomerId] = useState('')
  const [receiveDate, setReceiveDate] = useState(today())
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState('cash')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const selected = customers.find((c) => String(c.id) === customerId)

  useEffect(() => {
    apiClient
      .get('/fnb/config/pos-customers')
      .then((res) => setCustomers(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load customers'))
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/fnb/config/due-receives', {
        customer_id: customerId,
        receive_date: receiveDate,
        amount,
        method,
        notes,
      })
      router.push('/fnb/pos-customer/due-receive')
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
          <h1 className="text-3xl font-bold text-gray-900">Receive Due</h1>
          <p className="mt-1 text-gray-600">Collect outstanding from a POS credit customer.</p>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <form onSubmit={submit} className="mt-6 max-w-xl space-y-4 rounded-xl border bg-white p-6">
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Customer *</span>
              <select
                required
                className="w-full rounded-lg border px-3 py-2"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
              >
                <option value="">Select…</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                    {c.due_balance ? ` (due ${formatMoney(c.due_balance)})` : ''}
                  </option>
                ))}
              </select>
            </label>
            {selected && (
              <p className="text-sm text-slate-600">
                Outstanding: <strong>{formatMoney(selected.due_balance || 0)}</strong>
              </p>
            )}
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Date *</span>
              <input
                type="date"
                required
                className="w-full rounded-lg border px-3 py-2"
                value={receiveDate}
                onChange={(e) => setReceiveDate(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Amount *</span>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                className="w-full rounded-lg border px-3 py-2"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Method</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="cash">Cash</option>
                <option value="card">Card</option>
                <option value="bank">Bank</option>
                <option value="mobile">Mobile</option>
              </select>
            </label>
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Notes</span>
              <textarea
                className="w-full rounded-lg border px-3 py-2"
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </label>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Receive'}
            </button>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
