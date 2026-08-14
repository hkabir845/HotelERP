'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  TrendingUp,
  Search,
  RefreshCw,
  Download,
  DollarSign,
  Calendar,
  Filter,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Sale {
  id: number
  order_number: string
  date: string
  customer_name: string | null
  room_number: string | null
  revenue_center: string
  items_count: number
  subtotal: number
  tax: number
  discount: number
  total: number
  payment_method: string
}

export default function SalesListPage() {
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [dateFrom, setDateFrom] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
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
        date_to: dateTo
      })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/fnb/sales?${params.toString()}`)
      setSales(response.data.sales || [])
      setTotalPages(response.data.total_pages || 1)
    } catch (error) {
      console.error('Error fetching sales:', error)
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
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalSales = sales.reduce((sum, s) => sum + s.total, 0)
  const totalItems = sales.reduce((sum, s) => sum + s.items_count, 0)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Sales List</h1>
                    <p className="text-gray-600 mt-1">F&B sales and revenue tracking</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {}}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-200 flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Export
                  </button>
                  <button
                    onClick={fetchSales}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Sales</div>
                  <div className="text-2xl font-bold text-indigo-600 mt-1">{formatMoney(totalSales)}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Orders</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{sales.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Items Sold</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{totalItems}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Average Order</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {formatMoney(sales.length > 0 ? totalSales / sales.length : 0)}
                  </div>
                </div>
              </div>

              {/* Filters */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search by order #, customer, room..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => {
                        setDateFrom(e.target.value)
                        setCurrentPage(1)
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-gray-500">to</span>
                    <input
                      type="date"
                      value={dateTo}
                      onChange={(e) => {
                        setDateTo(e.target.value)
                        setCurrentPage(1)
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : sales.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <TrendingUp className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No sales found</h3>
                <p className="text-gray-600">No sales recorded for the selected period</p>
              </div>
            ) : (
              <>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer/Room</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue Center</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subtotal</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {sales.map((sale) => (
                          <tr key={sale.id} className="hover:bg-gray-200">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {sale.order_number}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatDate(sale.date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {sale.room_number ? `Room ${sale.room_number}` : sale.customer_name || 'Walk-in'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {sale.revenue_center}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {sale.items_count}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatMoney(sale.subtotal)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatMoney(sale.tax)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                              {formatMoney(sale.total)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                              {sale.payment_method}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                      Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                        disabled={currentPage === totalPages}
                        className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

