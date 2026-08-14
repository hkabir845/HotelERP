'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  Wrench,
  Search,
  Plus,
  RefreshCw,
  Eye,
  AlertCircle,
  CheckCircle2,
  Clock,
  User,
  Home
} from 'lucide-react'

interface MaintenanceRequest {
  id: number
  request_number: string
  asset_name: string
  asset_code: string
  location: string
  requested_by: string
  priority: string
  status: string
  issue_description: string
  requested_date: string
  assigned_to: string | null
  completed_date: string | null
}

export default function MaintenanceRequestsPage() {
  const router = useRouter()
  const [requests, setRequests] = useState<MaintenanceRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    assigned: { label: 'Assigned', color: 'text-blue-700', bgColor: 'bg-blue-100' },
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

  const fetchRequests = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (priorityFilter !== 'all') params.append('priority', priorityFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/assets/maintenance-requests?${params.toString()}`)
      setRequests(response.data.requests || [])
    } catch (error) {
      console.error('Error fetching maintenance requests:', error)
      setRequests([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRequests()
  }, [statusFilter, priorityFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchRequests(), 300)
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

  const pendingCount = requests.filter(r => r.status === 'pending' || r.status === 'assigned').length
  const urgentCount = requests.filter(r => r.priority === 'urgent' && r.status !== 'completed').length

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
                    <Wrench className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Maintenance Requests</h1>
                    <p className="text-gray-600 mt-1">Track and manage maintenance requests</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/assets/maintenance-requests/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Request
                  </button>
                  <button
                    onClick={fetchRequests}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Requests</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{requests.length}</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Pending</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">{pendingCount}</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Urgent</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{urgentCount}</div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Completed</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {requests.filter(r => r.status === 'completed').length}
                  </div>
                </div>
              </div>

              {urgentCount > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="font-medium text-red-900">
                      {urgentCount} urgent maintenance request{urgentCount !== 1 ? 's' : ''} require immediate attention
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
                        placeholder="Search by request #, asset, location..."
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
            ) : requests.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Wrench className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No maintenance requests</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new request</p>
                <button
                  onClick={() => router.push('/assets/maintenance-requests/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Request
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Request #</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested By</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned To</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested Date</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {requests.map((request) => {
                        const status = statusConfig[request.status] || statusConfig.pending
                        const priority = priorityConfig[request.priority] || priorityConfig.medium
                        return (
                          <tr key={request.id} className={request.priority === 'urgent' ? 'bg-red-50' : 'hover:bg-gray-200'}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {request.request_number}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">{request.asset_name}</div>
                              <div className="text-sm text-gray-500">{request.asset_code}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {request.location}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-1 text-sm text-gray-900">
                                <User className="h-3 w-3 text-gray-400" />
                                {request.requested_by}
                              </div>
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
                              {request.assigned_to || '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatDate(request.requested_date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <button
                                onClick={() => router.push(`/assets/maintenance-requests/${request.id}`)}
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

