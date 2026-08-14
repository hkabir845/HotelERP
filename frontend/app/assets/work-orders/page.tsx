'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  ClipboardCheck,
  Search,
  Plus,
  RefreshCw,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle,
  User,
  Wrench
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface WorkOrder {
  id: number
  work_order_number: string
  maintenance_request_id: number | null
  asset_name: string
  location: string
  assigned_to: string | null
  priority: string
  status: string
  estimated_cost: number
  actual_cost: number | null
  scheduled_date: string
  started_date: string | null
  completed_date: string | null
  description: string
}

export default function WorkOrdersPage() {
  const router = useRouter()
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    approved: { label: 'Approved', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    in_progress: { label: 'In Progress', color: 'text-indigo-700', bgColor: 'bg-indigo-100' },
    completed: { label: 'Completed', color: 'text-green-700', bgColor: 'bg-green-100' },
    cancelled: { label: 'Cancelled', color: 'text-gray-700', bgColor: 'bg-gray-100' }
  }

  const priorityConfig: Record<string, { label: string; color: string }> = {
    low: { label: 'Low', color: 'text-gray-600' },
    medium: { label: 'Medium', color: 'text-yellow-600' },
    high: { label: 'High', color: 'text-orange-600' },
    urgent: { label: 'Urgent', color: 'text-red-600' }
  }

  const fetchWorkOrders = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (priorityFilter !== 'all') params.append('priority', priorityFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/assets/work-orders?${params.toString()}`)
      setWorkOrders(response.data.work_orders || [])
    } catch (error) {
      console.error('Error fetching work orders:', error)
      setWorkOrders([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkOrders()
  }, [statusFilter, priorityFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchWorkOrders(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const pendingCount = workOrders.filter(wo => wo.status === 'pending' || wo.status === 'approved').length
  const urgentCount = workOrders.filter(wo => wo.priority === 'urgent' && wo.status !== 'completed').length
  const totalCost = workOrders.filter(wo => wo.actual_cost).reduce((sum, wo) => sum + (wo.actual_cost || 0), 0)

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
                    <ClipboardCheck className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Work Orders</h1>
                    <p className="text-gray-600 mt-1">Track and manage maintenance work orders</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/assets/work-orders/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Work Order
                  </button>
                  <button
                    onClick={fetchWorkOrders}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Work Orders</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{workOrders.length}</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Pending</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">{pendingCount}</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Urgent</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{urgentCount}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Cost</div>
                  <div className="text-2xl font-bold text-indigo-600 mt-1">{formatMoney(totalCost)}</div>
                </div>
              </div>

              {urgentCount > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="font-medium text-red-900">
                      {urgentCount} urgent work order{urgentCount !== 1 ? 's' : ''} require immediate attention
                    </span>
                  </div>
                </div>
              )}

              {/* Filters */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search by work order #, asset, location..."
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
                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="all">All Priorities</option>
                    {Object.entries(priorityConfig).map(([value, config]) => (
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
            ) : workOrders.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <ClipboardCheck className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No work orders found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new work order</p>
                <button
                  onClick={() => router.push('/assets/work-orders/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Work Order
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Work Order #</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned To</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {workOrders.map((wo) => {
                        const status = statusConfig[wo.status] || statusConfig.pending
                        const priority = priorityConfig[wo.priority] || priorityConfig.medium
                        return (
                          <tr key={wo.id} className={wo.priority === 'urgent' ? 'bg-red-50' : 'hover:bg-gray-200'}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {wo.work_order_number}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {wo.asset_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {wo.location}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {wo.assigned_to ? (
                                <div className="flex items-center gap-1 text-sm text-gray-900">
                                  <User className="h-3 w-3 text-gray-400" />
                                  {wo.assigned_to}
                                </div>
                              ) : (
                                <span className="text-sm text-gray-400">Unassigned</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`text-sm font-medium ${priority.color}`}>
                                {priority.label}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                                {status.label}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatDate(wo.scheduled_date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {wo.actual_cost ? (
                                <span>{formatMoney(wo.actual_cost)}</span>
                              ) : (
                                <span className="text-gray-400">Est: {formatMoney(wo.estimated_cost)}</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <button
                                onClick={() => router.push(`/assets/work-orders/${wo.id}`)}
                                className="text-indigo-600 hover:text-indigo-900"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

