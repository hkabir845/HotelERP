'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  Clock,
  Search,
  Plus,
  RefreshCw,
  CheckCircle2,
  Bell,
  User,
  Home,
  Calendar
} from 'lucide-react'

interface WakeUpCall {
  id: number
  room_number: string
  guest_name: string
  wake_up_time: string
  status: string
  completed_at: string | null
  notes: string | null
}

export default function WakeUpCallsPage() {
  const [calls, setCalls] = useState<WakeUpCall[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    scheduled: { label: 'Scheduled', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    completed: { label: 'Completed', color: 'text-green-700', bgColor: 'bg-green-100' },
    missed: { label: 'Missed', color: 'text-red-700', bgColor: 'bg-red-100' },
    cancelled: { label: 'Cancelled', color: 'text-gray-700', bgColor: 'bg-gray-100' }
  }

  const fetchWakeUpCalls = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/housekeeping/wake-up-calls?${params.toString()}`)
      setCalls(response.data.calls || [])
    } catch (error) {
      console.error('Error fetching wake-up calls:', error)
      setCalls([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWakeUpCalls()
    const interval = setInterval(fetchWakeUpCalls, 30000)
    return () => clearInterval(interval)
  }, [statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchWakeUpCalls(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const upcomingCalls = calls.filter(c => c.status === 'scheduled' && new Date(c.wake_up_time) > new Date())

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
                    <Bell className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Wake-up Calls</h1>
                    <p className="text-gray-600 mt-1">Manage guest wake-up call requests</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {}}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Call
                  </button>
                  <button
                    onClick={fetchWakeUpCalls}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Calls</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{calls.length}</div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Scheduled</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {calls.filter(c => c.status === 'scheduled').length}
                  </div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Completed</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {calls.filter(c => c.status === 'completed').length}
                  </div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Upcoming</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">{upcomingCalls.length}</div>
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
                        placeholder="Search by room, guest name..."
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
            ) : calls.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Bell className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No wake-up calls</h3>
                <p className="text-gray-600">No wake-up calls scheduled</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Wake-up Time</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {calls.map((call) => {
                        const status = statusConfig[call.status] || statusConfig.scheduled
                        return (
                          <tr key={call.id} className="hover:bg-gray-200">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <Home className="h-4 w-4 text-gray-400" />
                                <span className="text-sm font-medium text-gray-900">{call.room_number}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{call.guest_name}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-gray-400" />
                                <span className="text-sm font-medium text-gray-900">{formatTime(call.wake_up_time)}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatDate(call.wake_up_time)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                                {status.label}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {call.notes || '-'}
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

