'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { 
  Bed, 
  Search, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Wrench,
  RefreshCw,
  Calendar,
  User
} from 'lucide-react'
import {
  ROOM_STATUS_LABEL,
  roomStatusSoft,
  roomTileFill,
} from '@/lib/gyoroom-theme'

interface Room {
  id: number
  room_number: string
  floor: number | null
  room_type: {
    id: number
    name: string
    max_occupancy: number
  }
  status: string
  bed_type: string | null
  view: string | null
  housekeeping_status: string | null
  last_cleaned: string | null
  last_inspected: string | null
  next_cleaning_due: string | null
  has_pending_task: boolean
  task_type: string | null
  task_status: string | null
  notes: string | null
  is_active: boolean
}

interface RoomStatusSummary {
  available: number
  occupied: number
  cleaning: number
  maintenance: number
  out_of_order: number
  reserved: number
}

const STATUS_ICONS: Record<string, any> = {
  available: CheckCircle2,
  occupied: User,
  cleaning: RefreshCw,
  maintenance: Wrench,
  out_of_order: XCircle,
  reserved: Calendar,
}

const statusKeys = ['available', 'occupied', 'reserved', 'cleaning', 'maintenance', 'out_of_order'] as const

const housekeepingStatusConfig: Record<string, { label: string; color: string }> = {
  clean: { label: 'Clean', color: 'text-teal-600' },
  dirty: { label: 'Dirty', color: 'text-rose-600' },
  inspected: { label: 'Inspected', color: 'text-blue-600' },
  pending: { label: 'Pending', color: 'text-amber-600' },
}

export default function RoomStatusPage() {
  const [rooms, setRooms] = useState<Room[]>([])
  const [summary, setSummary] = useState<RoomStatusSummary>({
    available: 0,
    occupied: 0,
    cleaning: 0,
    maintenance: 0,
    out_of_order: 0,
    reserved: 0
  })
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [floorFilter, setFloorFilter] = useState<number | null>(null)
  const [roomTypeFilter, setRoomTypeFilter] = useState<number | null>(null)
  const [floors, setFloors] = useState<number[]>([])
  const [roomTypes, setRoomTypes] = useState<Array<{ id: number; name: string }>>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const fetchRooms = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (floorFilter !== null) params.append('floor', floorFilter.toString())
      if (roomTypeFilter !== null) params.append('room_type_id', roomTypeFilter.toString())
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/housekeeping/rooms/status?${params.toString()}`)
      setRooms(response.data.rooms || [])
      setSummary(response.data.summary || summary)
    } catch (error) {
      console.error('Error fetching rooms:', error)
      // Fallback to empty state
      setRooms([])
    } finally {
      setLoading(false)
    }
  }

  const fetchFilters = async () => {
    try {
      const [floorsRes, typesRes] = await Promise.all([
        apiClient.get('/housekeeping/rooms/floors'),
        apiClient.get('/housekeeping/rooms/types')
      ])
      setFloors(floorsRes.data.floors || [])
      setRoomTypes(typesRes.data.room_types || [])
    } catch (error) {
      console.error('Error fetching filters:', error)
    }
  }

  useEffect(() => {
    fetchRooms()
    fetchFilters()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchRooms, 30000)
    return () => clearInterval(interval)
  }, [statusFilter, floorFilter, roomTypeFilter])

  useEffect(() => {
    // Debounce search
    const timer = setTimeout(() => {
      fetchRooms()
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const filteredRooms = rooms.filter(room => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        room.room_number.toLowerCase().includes(search) ||
        room.room_type.name.toLowerCase().includes(search) ||
        (room.bed_type && room.bed_type.toLowerCase().includes(search)) ||
        (room.view && room.view.toLowerCase().includes(search))
      )
    }
    return true
  })

  const getStatusConfig = (status: string) => {
    const soft = roomStatusSoft(status)
    return {
      ...soft,
      label: ROOM_STATUS_LABEL[status] || soft.label,
      icon: STATUS_ICONS[status] || AlertCircle,
      fill: roomTileFill(status),
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <Bed className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Room Status</h1>
                    <p className="text-gray-600 mt-1">Monitor and manage room statuses in real-time</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    {viewMode === 'grid' ? 'List View' : 'Grid View'}
                  </button>
                  <button
                    onClick={fetchRooms}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                    title="Refresh"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards — solid GYOROOM status colors */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
                {statusKeys.map((status) => {
                  const config = getStatusConfig(status)
                  const count = summary[status as keyof RoomStatusSummary] ?? 0
                  return (
                    <button
                      key={status}
                      type="button"
                      className={`rounded-md px-3 py-3 text-left text-white shadow-sm transition-all hover:opacity-90 ${
                        statusFilter === status ? 'ring-2 ring-offset-2 ring-slate-700' : ''
                      }`}
                      style={{ backgroundColor: config.fill }}
                      onClick={() => setStatusFilter(statusFilter === status ? 'all' : status)}
                    >
                      <p className="text-xs font-medium uppercase tracking-wide opacity-90">{config.label}</p>
                      <p className="text-2xl font-bold mt-1">{count}</p>
                    </button>
                  )
                })}
              </div>

              {/* Filters */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="flex flex-wrap items-center gap-4">
                  {/* Search */}
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search by room number, type, bed, view..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Status Filter */}
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="all">All Statuses</option>
                    {statusKeys.map((value) => (
                      <option key={value} value={value}>{ROOM_STATUS_LABEL[value]}</option>
                    ))}
                  </select>

                  {/* Floor Filter */}
                  <select
                    value={floorFilter || ''}
                    onChange={(e) => setFloorFilter(e.target.value ? parseInt(e.target.value) : null)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="">All Floors</option>
                    {floors.map(floor => (
                      <option key={floor} value={floor}>Floor {floor}</option>
                    ))}
                  </select>

                  {/* Room Type Filter */}
                  <select
                    value={roomTypeFilter || ''}
                    onChange={(e) => setRoomTypeFilter(e.target.value ? parseInt(e.target.value) : null)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="">All Types</option>
                    {roomTypes.map(type => (
                      <option key={type.id} value={type.id}>{type.name}</option>
                    ))}
                  </select>

                  {/* Clear Filters */}
                  {(statusFilter !== 'all' || floorFilter !== null || roomTypeFilter !== null || searchTerm) && (
                    <button
                      onClick={() => {
                        setStatusFilter('all')
                        setFloorFilter(null)
                        setRoomTypeFilter(null)
                        setSearchTerm('')
                      }}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Rooms Display */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : filteredRooms.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Bed className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No rooms found</h3>
                <p className="text-gray-600">Try adjusting your filters or search terms</p>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex flex-wrap gap-2 mb-4">
                  {statusKeys.map((status) => {
                    const config = getStatusConfig(status)
                    return (
                      <span
                        key={status}
                        className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-700"
                      >
                        <span
                          className="inline-block h-3 w-3 rounded-sm"
                          style={{ backgroundColor: config.fill }}
                        />
                        {config.label}
                      </span>
                    )
                  })}
                </div>
                <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-2">
                  {filteredRooms.map((room) => {
                    const config = getStatusConfig(room.status)
                    return (
                      <button
                        key={room.id}
                        type="button"
                        title={`${room.room_number} · ${config.label}${room.room_type?.name ? ` · ${room.room_type.name}` : ''}`}
                        className={`min-h-[52px] rounded px-1 py-2 text-center text-white shadow-sm transition hover:brightness-110 ${
                          statusFilter === room.status ? 'ring-2 ring-slate-800 ring-offset-1' : ''
                        }`}
                        style={{ backgroundColor: config.fill }}
                      >
                        <div className="text-sm font-bold leading-tight">{room.room_number}</div>
                        <div className="text-[10px] opacity-90 truncate">{config.label}</div>
                      </button>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Room
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Housekeeping
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Cleaned
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Details
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredRooms.map((room) => {
                      const statusConfig = getStatusConfig(room.status)
                      const StatusIcon = statusConfig.icon
                      const hkStatus = room.housekeeping_status
                      const hkConfig = hkStatus ? housekeepingStatusConfig[hkStatus] : null

                      return (
                        <tr key={room.id} className="hover:bg-gray-200">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <StatusIcon className={`h-5 w-5 ${statusConfig.color} mr-2`} />
                              <div>
                                <div className="text-sm font-medium text-gray-900">{room.room_number}</div>
                                {room.floor && (
                                  <div className="text-sm text-gray-500">Floor {room.floor}</div>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{room.room_type.name}</div>
                            <div className="text-sm text-gray-500">
                              {room.bed_type} {room.view && `• ${room.view}`}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-semibold rounded text-white"
                              style={{ backgroundColor: statusConfig.fill }}
                            >
                              <StatusIcon className="h-3.5 w-3.5" />
                              {statusConfig.label}
                            </span>
                            {room.has_pending_task && (
                              <div className="mt-1 text-xs text-amber-600">Pending Task</div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {hkConfig ? (
                              <span className={`text-sm font-medium ${hkConfig.color}`}>
                                {hkConfig.label}
                              </span>
                            ) : (
                              <span className="text-sm text-gray-400">N/A</span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {room.last_cleaned ? formatDate(room.last_cleaned) : 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {room.notes ? (
                              <span className="truncate max-w-xs block" title={room.notes}>
                                {room.notes}
                              </span>
                            ) : (
                              '-'
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Footer Stats */}
            <div className="mt-6 text-center text-sm text-gray-600">
              Showing {filteredRooms.length} of {rooms.length} rooms
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
