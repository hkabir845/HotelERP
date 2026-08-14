'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

type Props = {
  title: string
  subtitle?: string
  query: Record<string, string>
  emptyText?: string
}

export default function ReservationFilterPage({ title, subtitle, query, emptyText }: Props) {
  const router = useRouter()
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    const params = new URLSearchParams({ limit: '200', ...query })
    apiClient
      .get(`/reservations?${params.toString()}`)
      .then((res) => setRows(res.data.reservations || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [JSON.stringify(query)])

  const money = (n: number | null | undefined) => formatMoney(n || 0)
  const day = (value: string | null | undefined) => {
    if (!value) return ''
    return new Date(value).toLocaleDateString()
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="mt-1 text-gray-600">{subtitle}</p>}
          {error && <p className="mt-3 text-red-600">{error}</p>}
          <div className="mt-6 overflow-hidden rounded-xl border bg-white">
            {loading ? (
              <p className="px-4 py-8 text-center text-slate-500">Loading…</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-4 py-3">Reservation</th>
                    <th className="px-4 py-3">Guest</th>
                    <th className="px-4 py-3">Room</th>
                    <th className="px-4 py-3">Check-in</th>
                    <th className="px-4 py-3">Check-out</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Total</th>
                    <th className="px-4 py-3">Balance</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={9} className="px-4 py-8 text-center text-slate-500">
                        {emptyText || 'No records found.'}
                      </td>
                    </tr>
                  )}
                  {rows.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-4 py-3 font-medium">{row.reservation_number}</td>
                      <td className="px-4 py-3">{row.guest?.name || ''}</td>
                      <td className="px-4 py-3">{row.room?.room_number || '—'}</td>
                      <td className="px-4 py-3">{day(row.check_in_date)}</td>
                      <td className="px-4 py-3">{day(row.check_out_date)}</td>
                      <td className="px-4 py-3">{row.status}</td>
                      <td className="px-4 py-3">{money(row.total_amount)}</td>
                      <td className="px-4 py-3">{money(row.balance)}</td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          className="text-indigo-700 hover:underline"
                          onClick={() => router.push(`/frontdesk/reservations/${row.id}`)}
                        >
                          Folio
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
