'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

function money(n: any) {
  return formatMoney(n || 0)
}

export default function HrBulkPaymentPage() {
  const [items, setItems] = useState<any[]>([])
  const [method, setMethod] = useState('bank')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = () => {
    apiClient
      .get('/hr/payroll')
      .then((res) => setItems((res.data.items || []).filter((r: any) => r.can_pay)))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [])

  const payAll = async () => {
    setError('')
    setMessage('')
    try {
      const res = await apiClient.post('/hr/payroll/bulk-pay', { method })
      setMessage(`Paid ${res.data.paid} payroll slip(s).`)
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Bulk pay failed')
    }
  }

  const total = items.reduce((sum, row) => sum + Number(row.net_pay || 0), 0)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Bulk Payment</h1>
          <p className="mt-1 text-gray-600">Pay all approved payroll slips in one posting.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {message && <p className="mt-4 text-emerald-700">{message}</p>}
          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Method</span>
              <select className="rounded-lg border px-3 py-2" value={method} onChange={(e) => setMethod(e.target.value)}>
                <option value="bank">Bank</option>
                <option value="cash">Cash</option>
                <option value="mobile">Mobile</option>
              </select>
            </label>
            <div className="text-sm">
              <div className="text-slate-500">Approved net</div>
              <div className="font-semibold">{money(total)}</div>
            </div>
            <button
              type="button"
              onClick={payAll}
              disabled={items.length === 0}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              Pay all approved
            </button>
          </div>
          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {['Payroll', 'Employee', 'Period', 'Net'].map((h) => (
                    <th key={h} className="px-3 py-2 font-medium">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-10 text-center text-slate-500">
                      No approved slips waiting for payment.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-3 py-2">{row.payroll_number}</td>
                      <td className="px-3 py-2">{row.employee_name}</td>
                      <td className="px-3 py-2">
                        {row.pay_period_start} → {row.pay_period_end}
                      </td>
                      <td className="px-3 py-2 text-right">{money(row.net_pay)}</td>
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
