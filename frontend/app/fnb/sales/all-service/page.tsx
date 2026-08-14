'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Search, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'

type Sale = {
  id: number
  order_number: string
  date: string
  customer_name: string | null
  room_number: string | null
  revenue_center: string
  order_type: string
  source: string
  status: string
  items_count: number
  subtotal: number
  tax: number
  discount: number
  total: number
  paid: number
  due: number
  payment_method: string
  payment_status: string
}

export default function Page() {
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [dateFrom, setDateFrom] = useState(
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [dateTo, setDateTo] = useState(new Date().toISOString().split('T')[0])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchSales = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        date_from: dateFrom,
        date_to: dateTo,
        all_service: '1',
      })
      if (searchTerm) params.append('search', searchTerm)
      const response = await apiClient.get(`/fnb/sales?${params.toString()}`)
      setSales(response.data.sales || [])
      setTotalPages(response.data.total_pages || 1)
    } catch {
      setSales([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSales()
  }, [currentPage, dateFrom, dateTo])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) fetchSales()
      else setCurrentPage(1)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const money = (n: number) => formatMoney(n || 0)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Sales List [All Service]</h1>
          <p className="mt-1 text-gray-600">
            All outlets, sources, and statuses including cancelled tickets.
          </p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <div className="relative min-w-[220px] flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                className="w-full rounded-lg border py-2 pl-9 pr-3 text-sm"
                placeholder="Order, customer, room…"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <input
              type="date"
              className="rounded-lg border px-3 py-2 text-sm"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value)
                setCurrentPage(1)
              }}
            />
            <input
              type="date"
              className="rounded-lg border px-3 py-2 text-sm"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value)
                setCurrentPage(1)
              }}
            />
            <button
              type="button"
              onClick={fetchSales}
              className="rounded-lg border bg-white p-2 text-gray-600"
            >
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : sales.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No sales in this period.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    {[
                      'Order',
                      'Date',
                      'Customer / room',
                      'Center',
                      'Type',
                      'Source',
                      'Status',
                      'Items',
                      'Total',
                      'Paid',
                      'Due',
                      'Pay',
                    ].map((h) => (
                      <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sales.map((sale) => (
                    <tr key={sale.id} className="border-t">
                      <td className="px-3 py-2 font-medium">{sale.order_number}</td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        {new Date(sale.date).toLocaleString()}
                      </td>
                      <td className="px-3 py-2">
                        {sale.room_number
                          ? `Room ${sale.room_number}`
                          : sale.customer_name || 'Walk-in'}
                      </td>
                      <td className="px-3 py-2">{sale.revenue_center}</td>
                      <td className="px-3 py-2">{sale.order_type}</td>
                      <td className="px-3 py-2">{sale.source}</td>
                      <td className="px-3 py-2">{sale.status}</td>
                      <td className="px-3 py-2 text-right">{sale.items_count}</td>
                      <td className="px-3 py-2 text-right">{money(sale.total)}</td>
                      <td className="px-3 py-2 text-right">{money(sale.paid)}</td>
                      <td className="px-3 py-2 text-right">{money(sale.due)}</td>
                      <td className="px-3 py-2 capitalize">{sale.payment_status || sale.payment_method}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between text-sm">
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="rounded border p-2 disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  className="rounded border p-2 disabled:opacity-50"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
