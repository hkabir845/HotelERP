'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  ClipboardList,
  Search,
  Filter,
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  User,
  Home,
  RefreshCw,
  Calendar
} from 'lucide-react'

interface Task {
  id: number
  task_number: string
  room: {
    id: number
    room_number: string
    room_type: string
  }
  task_type: string
  status: string
  priority: string
  assigned_to: {
    id: number
    name: string
  } | null
  scheduled_date: string
  started_at: string | null
  completed_at: string | null
  description: string | null
}

export default function HousekeepingTasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    in_progress: { label: 'In Progress', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    completed: { label: 'Completed', color: 'text-green-700', bgColor: 'bg-green-100' },
    cancelled: { label: 'Cancelled', color: 'text-gray-700', bgColor: 'bg-gray-100' }
  }

  const priorityConfig: Record<string, { label: string; color: string }> = {
    low: { label: 'Low', color: 'text-gray-600' },
    medium: { label: 'Medium', color: 'text-yellow-600' },
    high: { label: 'High', color: 'text-orange-600' },
    urgent: { label: 'Urgent', color: 'text-red-600' }
  }

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (priorityFilter !== 'all') params.append('priority', priorityFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/housekeeping/tasks?${params.toString()}`)
      setTasks(response.data.tasks || [])
    } catch (error) {
      console.error('Error fetching tasks:', error)
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
    const interval = setInterval(fetchTasks, 30000)
    return () => clearInterval(interval)
  }, [statusFilter, priorityFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchTasks(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const pendingTasks = tasks.filter(t => t.status === 'pending' || t.status === 'in_progress').length

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
                    <ClipboardList className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Housekeeping Tasks</h1>
                    <p className="text-gray-600 mt-1">Manage and track housekeeping tasks</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {}}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Task
                  </button>
                  <button
                    onClick={fetchTasks}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Tasks</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{tasks.length}</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Pending</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">
                    {tasks.filter(t => t.status === 'pending').length}
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">In Progress</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {tasks.filter(t => t.status === 'in_progress').length}
                  </div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Completed</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {tasks.filter(t => t.status === 'completed').length}
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
                        placeholder="Search by room, task type, assigned to..."
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
            ) : tasks.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <ClipboardList className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
                <p className="text-gray-600">Get started by creating a new task</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks.map((task) => {
                  const status = statusConfig[task.status] || statusConfig.pending
                  const priority = priorityConfig[task.priority] || priorityConfig.medium
                  return (
                    <div key={task.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="text-sm font-medium text-gray-500">Task #</div>
                          <div className="text-lg font-bold text-gray-900">{task.task_number}</div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                          {status.label}
                        </span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm text-gray-600">Room</div>
                          <div className="text-base font-medium text-gray-900 flex items-center gap-2">
                            <Home className="h-4 w-4" />
                            {task.room.room_number} - {task.room.room_type}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm text-gray-600">Task Type</div>
                          <div className="text-base font-medium text-gray-900 capitalize">{task.task_type.replace('_', ' ')}</div>
                        </div>

                        <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                          <div>
                            <div className="text-sm text-gray-600">Priority</div>
                            <div className={`text-sm font-medium ${priority.color}`}>
                              {priority.label}
                            </div>
                          </div>
                          {task.assigned_to && (
                            <div>
                              <div className="text-sm text-gray-600">Assigned To</div>
                              <div className="text-sm font-medium text-gray-900 flex items-center gap-1">
                                <User className="h-3 w-3" />
                                {task.assigned_to.name}
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="pt-3 border-t border-gray-200">
                          <div className="text-sm text-gray-600">Scheduled</div>
                          <div className="text-sm font-medium text-gray-900 flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {formatDate(task.scheduled_date)}
                          </div>
                        </div>

                        {task.description && (
                          <div className="pt-3 border-t border-gray-200">
                            <div className="text-sm text-gray-600">Description</div>
                            <div className="text-sm text-gray-900">{task.description}</div>
                          </div>
                        )}

                        {task.completed_at && (
                          <div className="pt-3 border-t border-gray-200">
                            <div className="text-sm text-gray-600">Completed</div>
                            <div className="text-sm font-medium text-green-600 flex items-center gap-1">
                              <CheckCircle2 className="h-3 w-3" />
                              {formatDate(task.completed_at)}
                            </div>
                          </div>
                        )}
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

