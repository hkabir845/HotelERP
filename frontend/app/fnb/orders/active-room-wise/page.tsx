'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  UtensilsCrossed,
  Search,
  RefreshCw,
  Home,
  User,
  Clock
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Order {
  id: number
  order_number: string
  room_number: string
  guest_name: string
  status: string
  total: number
  created_at: string
  items_count: number
}

export default function ActiveOrdersRoomWisePage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ status: 'active', order_type: 'room' })
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
  }, [])

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

  // Group by room
  const ordersByRoom = orders.reduce((acc, order) => {
    if (!acc[order.room_number]) {
      acc[order.room_number] = []
    }
    acc[order.room_number].push(order)
    return acc
  }, {} as Record<string, Order[]>)

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
                    <h1 className="text-3xl font-bold text-gray-900">Active Orders (Room Wise)</h1>
                    <p className="text-gray-600 mt-1">F&B orders organized by room</p>
                  </div>
                </div>
                <button
                  onClick={fetchOrders}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by room number, guest name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : Object.keys(ordersByRoom).length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <UtensilsCrossed className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No active room orders</h3>
                <p className="text-gray-600">No room service orders currently active</p>
              </div>
            ) : (
              <div className="space-y-6">
                {Object.entries(ordersByRoom).map(([roomNumber, roomOrders]) => (
                  <div key={roomNumber} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Home className="h-5 w-5 text-indigo-600" />
                      <h2 className="text-xl font-semibold text-gray-900">Room {roomNumber}</h2>
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-700">
                        {roomOrders.length} order{roomOrders.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="space-y-3">
                      {roomOrders.map((order) => (
                        <div key={order.id} className="flex items-center justify-between p-4 bg-gray-200 rounded-lg">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">{order.order_number}</div>
                            <div className="text-sm text-gray-500 flex items-center gap-4 mt-1">
                              <span className="flex items-center gap-1">
                                <User className="h-3 w-3" />
                                {order.guest_name}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatDate(order.created_at)}
                              </span>
                              <span>{order.items_count} items</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-indigo-600">{formatMoney(order.total)}</div>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              order.status === 'ready' ? 'bg-green-100 text-green-700' :
                              order.status === 'preparing' ? 'bg-blue-100 text-blue-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>
                              {order.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

