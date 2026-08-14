'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function WebsiteBookingsPage() {
  const [bookings, setBookings] = useState<any[]>([])
  const [orders, setOrders] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get('/website/bookings')
      .then((res) => {
        setBookings(res.data.bookings || [])
        setOrders(res.data.orders || [])
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load website bookings'))
  }, [])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Website bookings</h1>
          <p className="mt-1 text-gray-600">Reservations and dining orders placed from the public site.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}

          <h2 className="mt-8 text-lg font-semibold">Room bookings</h2>
          <div className="mt-3 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3">Number</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Check-in</th>
                  <th className="px-4 py-3">Amount</th>
                </tr>
              </thead>
              <tbody>
                {bookings.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                      No website reservations yet.
                    </td>
                  </tr>
                )}
                {bookings.map((b) => (
                  <tr key={b.id} className="border-t">
                    <td className="px-4 py-3 font-medium">{b.reservation_number}</td>
                    <td className="px-4 py-3">{b.status}</td>
                    <td className="px-4 py-3">{String(b.check_in_date || '').slice(0, 10)}</td>
                    <td className="px-4 py-3">{b.total_amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2 className="mt-8 text-lg font-semibold">Dining orders</h2>
          <div className="mt-3 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3">Number</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Payment</th>
                  <th className="px-4 py-3">Amount</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                      No website dining orders yet.
                    </td>
                  </tr>
                )}
                {orders.map((o) => (
                  <tr key={o.id} className="border-t">
                    <td className="px-4 py-3 font-medium">{o.order_number}</td>
                    <td className="px-4 py-3">{o.status}</td>
                    <td className="px-4 py-3">{o.payment_status}</td>
                    <td className="px-4 py-3">{o.total_amount}</td>
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
