'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  UtensilsCrossed,
  Search,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  Eye,
  User,
  Phone
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Order {
  id: number
  order_number: string
  order_type: string
  customer_name: string | null
  customer_phone: string | null
  room_number: string | null
  table_number?: string | null
  requested_at?: string | null
  status: string
  total: number
  created_at: string
  items_count: number
}

export default function ActiveOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    confirmed: { label: 'Confirmed', color: 'text-sky-700', bgColor: 'bg-sky-100' },
    preparing: { label: 'Preparing', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    ready: { label: 'Ready', color: 'text-green-700', bgColor: 'bg-green-100' },
    completed: { label: 'Completed', color: 'text-gray-700', bgColor: 'bg-gray-100' },
    cancelled: { label: 'Cancelled', color: 'text-red-700', bgColor: 'bg-red-100' }
  }

  const runAction = async (id: number, action: string) => {
    try {
      await apiClient.post(`/fnb/orders/${id}/action`, { action })
      fetchOrders()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Action failed')
    }
  }

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ status: 'active' })
      if (statusFilter !== 'all') params.append('status_filter', statusFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/fnb/orders?${params.toString()}`)
      setOrders(response.data.orders || [])
    } catch (error) {
      console.error('Error fetching orders:', error)
      setOrders([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
    const interval = setInterval(fetchOrders, 30000)
    return () => clearInterval(interval)
  }, [statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchOrders(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const activeOrders = orders.filter(o => o.status !== 'completed' && o.status !== 'cancelled')

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
                    <UtensilsCrossed className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Active Orders</h1>
                    <p className="text-gray-600 mt-1">All active F&B orders</p>
                  </div>
                </div>
                <button
                  onClick={fetchOrders}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Active</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{activeOrders.length}</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Pending</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">
                    {orders.filter(o => o.status === 'pending').length}
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Preparing</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {orders.filter(o => o.status === 'preparing').length}
                  </div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Ready</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {orders.filter(o => o.status === 'ready').length}
                  </div>
                </div>
              </div>

              {/* Filters */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
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
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="all">All Statuses</option>
                    {Object.entries(statusConfig).map(([value, config]) => (
                      <option key={value} value={value}>{config.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : activeOrders.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <UtensilsCrossed className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No active orders</h3>
                <p className="text-gray-600">All orders have been completed or cancelled</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {activeOrders.map((order) => {
                  const status = statusConfig[order.status] || statusConfig.pending
                  return (
                    <div key={order.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="text-sm font-medium text-gray-500">Order #</div>
                          <div className="text-lg font-bold text-gray-900">{order.order_number}</div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                          {status.label}
                        </span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm text-gray-600">Type</div>
                          <div className="text-sm font-medium text-gray-900 capitalize">{order.order_type.replace('_', ' ')}</div>
                        </div>

                        {order.room_number ? (
                          <div>
                            <div className="text-sm text-gray-600">Room</div>
                            <div className="text-sm font-medium text-gray-900">{order.room_number}</div>
                          </div>
                        ) : (
                          <div>
                            <div className="text-sm text-gray-600">Customer</div>
                            <div className="text-sm font-medium text-gray-900">{order.customer_name || 'N/A'}</div>
                            {order.customer_phone && (
                              <div className="text-xs text-gray-500">{order.customer_phone}</div>
                            )}
                            {order.table_number && (
                              <div className="text-xs text-gray-500">Table {order.table_number}</div>
                            )}
                          </div>
                        )}

                        {order.requested_at && (
                          <div>
                            <div className="text-sm text-gray-600">Serve at</div>
                            <div className="text-sm font-medium text-gray-900">{formatDate(order.requested_at)}</div>
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
                          <div>
                            <div className="text-sm text-gray-600">Items</div>
                            <div className="text-sm font-medium text-gray-900">{order.items_count}</div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-600">Total</div>
                            <div className="text-sm font-medium text-indigo-600">{formatMoney(order.total)}</div>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-200">
                          {order.status === 'pending' && (
                            <button type="button" className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs text-white" onClick={() => runAction(order.id, 'confirm')}>Confirm</button>
                          )}
                          {(order.status === 'pending' || order.status === 'confirmed') && (
                            <button type="button" className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs text-white" onClick={() => runAction(order.id, 'prepare')}>Prepare</button>
                          )}
                          {order.status === 'preparing' && (
                            <button type="button" className="rounded-lg bg-green-600 px-3 py-1.5 text-xs text-white" onClick={() => runAction(order.id, 'ready')}>Ready</button>
                          )}
                          {order.status === 'ready' && (
                            <button type="button" className="rounded-lg bg-emerald-700 px-3 py-1.5 text-xs text-white" onClick={() => runAction(order.id, 'complete')}>Serve / complete</button>
                          )}
                          {order.status !== 'completed' && order.status !== 'cancelled' && (
                            <button type="button" className="rounded-lg border px-3 py-1.5 text-xs" onClick={() => runAction(order.id, 'cancel')}>Cancel</button>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

