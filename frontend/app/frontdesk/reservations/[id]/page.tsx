'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

export default function FolioPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const [charge, setCharge] = useState({ description: '', amount: '' })
  const [payment, setPayment] = useState({ amount: '', payment_method: 'cash', description: '' })

  const load = () => {
    apiClient
      .get(`/reservations/${id}`)
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load folio'))
  }

  useEffect(() => {
    load()
  }, [id])

  const run = async (path: string, body?: any) => {
    setBusy(path)
    setError('')
    try {
      const res = await apiClient.post(`/reservations/${id}/${path}`, body || {})
      setData(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    } finally {
      setBusy('')
    }
  }

  const addLine = async (action: 'charge' | 'payment') => {
    setBusy(action)
    setError('')
    try {
      const body =
        action === 'charge'
          ? { action: 'charge', description: charge.description, amount: charge.amount }
          : { action: 'payment', amount: payment.amount, payment_method: payment.payment_method, description: payment.description }
      const res = await apiClient.post(`/reservations/${id}/folio`, body)
      setData(res.data)
      if (action === 'charge') setCharge({ description: '', amount: '' })
      else setPayment({ amount: '', payment_method: 'cash', description: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setBusy('')
    }
  }

  const money = (n: number) => formatMoney(n || 0)
  const res = data?.reservation
  const folio = data?.folio
  const status = res?.status

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <button type="button" onClick={() => router.back()} className="mb-3 text-sm text-indigo-700">
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Guest Folio</h1>
          <p className="mt-1 text-gray-600">{res?.reservation_number || 'Loading…'}</p>
          {error && <p className="mt-3 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

          {res && (
            <>
              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <div className="rounded-xl border bg-white p-4">
                  <div className="text-sm text-gray-500">Guest</div>
                  <div className="font-semibold">{res.guest?.name}</div>
                  <div className="text-sm text-gray-500">{res.guest?.phone}</div>
                </div>
                <div className="rounded-xl border bg-white p-4">
                  <div className="text-sm text-gray-500">Room</div>
                  <div className="font-semibold">{res.room?.room_number || 'Not assigned'}</div>
                  <div className="text-sm text-gray-500">{res.room?.room_type}</div>
                </div>
                <div className="rounded-xl border bg-white p-4">
                  <div className="text-sm text-gray-500">Stay</div>
                  <div className="font-semibold">{res.nights} night(s)</div>
                  <div className="text-sm text-gray-500">{status?.replace('_', ' ')}</div>
                </div>
                <div className="rounded-xl border bg-white p-4">
                  <div className="text-sm text-gray-500">Balance</div>
                  <div className={`text-2xl font-bold ${(folio?.balance || 0) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {money(folio?.balance)}
                  </div>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {(status === 'confirmed' || status === 'pending') && (
                  <button
                    disabled={!!busy}
                    onClick={() => run('check-in')}
                    className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white disabled:opacity-50"
                  >
                    {busy === 'check-in' ? 'Checking in…' : 'Check in'}
                  </button>
                )}
                {status === 'checked_in' && (
                  <>
                    <button
                      disabled={!!busy}
                      onClick={() => run('check-out')}
                      className="rounded-lg bg-orange-600 px-4 py-2 text-sm text-white disabled:opacity-50"
                    >
                      {busy === 'check-out' ? 'Checking out…' : 'Check out'}
                    </button>
                    {(folio?.balance || 0) > 0 && (
                      <button
                        disabled={!!busy}
                        onClick={() => run('check-out', { force: true })}
                        className="rounded-lg border border-orange-300 px-4 py-2 text-sm text-orange-800 disabled:opacity-50"
                      >
                        Check out with balance
                      </button>
                    )}
                  </>
                )}
                {(status === 'confirmed' || status === 'pending') && (
                  <>
                    <button
                      disabled={!!busy}
                      onClick={() => run('cancel', { status: 'cancelled' })}
                      className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button
                      disabled={!!busy}
                      onClick={() => run('cancel', { status: 'no_show' })}
                      className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50"
                    >
                      No show
                    </button>
                  </>
                )}
              </div>

              <div className="mt-6 grid gap-6 lg:grid-cols-2">
                <div className="rounded-xl border bg-white p-4">
                  <h2 className="font-semibold">Charges</h2>
                  <table className="mt-3 w-full text-sm">
                    <tbody>
                      {(folio?.charges || []).map((row: any) => (
                        <tr key={row.id} className="border-t">
                          <td className="py-2">{row.description}</td>
                          <td className="py-2 text-right">{money(row.amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <form
                    className="mt-4 grid gap-2 sm:grid-cols-3"
                    onSubmit={(e) => {
                      e.preventDefault()
                      addLine('charge')
                    }}
                  >
                    <input
                      required
                      placeholder="Extra charge"
                      className="rounded-lg border px-3 py-2 sm:col-span-2"
                      value={charge.description}
                      onChange={(e) => setCharge((p) => ({ ...p, description: e.target.value }))}
                    />
                    <input
                      required
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="Amount"
                      className="rounded-lg border px-3 py-2"
                      value={charge.amount}
                      onChange={(e) => setCharge((p) => ({ ...p, amount: e.target.value }))}
                    />
                    <button disabled={!!busy} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white sm:col-span-3">
                      Add charge
                    </button>
                  </form>
                </div>

                <div className="rounded-xl border bg-white p-4">
                  <h2 className="font-semibold">Payments</h2>
                  <table className="mt-3 w-full text-sm">
                    <tbody>
                      {(folio?.payments || []).map((row: any) => (
                        <tr key={row.id} className="border-t">
                          <td className="py-2">{row.description} ({row.method})</td>
                          <td className="py-2 text-right">{money(row.amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <form
                    className="mt-4 grid gap-2 sm:grid-cols-3"
                    onSubmit={(e) => {
                      e.preventDefault()
                      addLine('payment')
                    }}
                  >
                    <input
                      required
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="Amount"
                      className="rounded-lg border px-3 py-2"
                      value={payment.amount}
                      onChange={(e) => setPayment((p) => ({ ...p, amount: e.target.value }))}
                    />
                    <select
                      className="rounded-lg border px-3 py-2"
                      value={payment.payment_method}
                      onChange={(e) => setPayment((p) => ({ ...p, payment_method: e.target.value }))}
                    >
                      <option value="cash">Cash</option>
                      <option value="card">Card</option>
                      <option value="bank_transfer">Bank</option>
                      <option value="wallet">Mobile / wallet</option>
                    </select>
                    <input
                      placeholder="Note"
                      className="rounded-lg border px-3 py-2"
                      value={payment.description}
                      onChange={(e) => setPayment((p) => ({ ...p, description: e.target.value }))}
                    />
                    <button disabled={!!busy} className="rounded-lg bg-green-600 px-3 py-2 text-sm text-white sm:col-span-3">
                      Collect payment
                    </button>
                  </form>
                </div>
              </div>

              <div className="mt-4 rounded-xl border bg-white p-4 text-sm">
                <div className="flex justify-between"><span>Total</span><span>{money(folio?.total_amount)}</span></div>
                <div className="flex justify-between"><span>Paid</span><span>{money(folio?.paid_amount)}</span></div>
                <div className="mt-2 flex justify-between border-t pt-2 font-semibold">
                  <span>Balance</span>
                  <span>{money(folio?.balance)}</span>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
