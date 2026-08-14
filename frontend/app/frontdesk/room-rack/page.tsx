'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { 
  Home, 
  Search, 
  Filter, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertCircle,
  Wrench,
  User,
  Calendar,
  RefreshCw,
  Bed,
  Users,
  DollarSign,
  Eye,
  ChevronLeft,
  ChevronRight,
  CalendarDays
} from 'lucide-react'
import { formatMoney } from '@/lib/money'
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
    base_rate: number | null
  }
  status: string
  bed_type: string | null
  view: string | null
  rack_rate: number | null
  is_active: boolean
  current_reservation: {
    id: number
    reservation_number: string
    guest: {
      id: number
      name: string
      first_name: string
      last_name: string
      phone: string | null
      email: string | null
      is_vip: boolean
    }
    check_in_date: string
    check_out_date: string
    actual_check_in: string | null
    actual_check_out: string | null
    status: string
    reservation_type: string
    adults: number
    children: number
    room_rate: number | null
    total_amount: number | null
    paid_amount: number | null
    balance: number | null
    source: string | null
    nights: number
  } | null
  all_reservations: Array<{
    id: number
    reservation_number: string
    guest_name: string
    check_in_date: string
    check_out_date: string
    status: string
    nights: number
  }>
}

interface RoomRackSummary {
  available: number
  occupied: number
  reserved: number
  out_of_order: number
  maintenance: number
  cleaning: number
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

function getStatusConfig(status: string) {
  const soft = roomStatusSoft(status)
  return {
    ...soft,
    label: ROOM_STATUS_LABEL[status] || soft.label,
    icon: STATUS_ICONS[status] || AlertCircle,
    fill: roomTileFill(status),
  }
}

export default function RoomRackPage() {
  const router = useRouter()
  const [rooms, setRooms] = useState<Room[]>([])
  const [summary, setSummary] = useState<RoomRackSummary>({
    available: 0,
    occupied: 0,
    reserved: 0,
    out_of_order: 0,
    maintenance: 0,
    cleaning: 0
  })
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [floorFilter, setFloorFilter] = useState<number | null>(null)
  const [roomTypeFilter, setRoomTypeFilter] = useState<number | null>(null)
  const [floors, setFloors] = useState<number[]>([])
  const [roomTypes, setRoomTypes] = useState<Array<{ id: number; name: string }>>([])
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [viewMode, setViewMode] = useState<'rack' | 'grid'>('rack')
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)

  const fetchRoomRack = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (floorFilter !== null) params.append('floor', floorFilter.toString())
      if (roomTypeFilter !== null) params.append('room_type_id', roomTypeFilter.toString())
      if (searchTerm) params.append('search', searchTerm)
      if (selectedDate) params.append('date_filter', selectedDate)

      const response = await apiClient.get(`/frontdesk/room-rack?${params.toString()}`)
      setRooms(response.data.rooms || [])
      setSummary(response.data.summary || summary)
    } catch (error) {
      console.error('Error fetching room rack:', error)
      setRooms([])
    } finally {
      setLoading(false)
    }
  }

  const fetchFilters = async () => {
    try {
      const [floorsRes, typesRes] = await Promise.all([
        apiClient.get('/frontdesk/room-rack/floors'),
        apiClient.get('/frontdesk/room-rack/types')
      ])
      setFloors(floorsRes.data.floors || [])
      setRoomTypes(typesRes.data.room_types || [])
    } catch (error) {
      console.error('Error fetching filters:', error)
    }
  }

  useEffect(() => {
    fetchRoomRack()
    fetchFilters()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchRoomRack, 30000)
    return () => clearInterval(interval)
  }, [statusFilter, floorFilter, roomTypeFilter, selectedDate])

  useEffect(() => {
    // Debounce search
    const timer = setTimeout(() => {
      fetchRoomRack()
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
  }

  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const changeDate = (days: number) => {
    const currentDate = new Date(selectedDate)
    currentDate.setDate(currentDate.getDate() + days)
    setSelectedDate(currentDate.toISOString().split('T')[0])
  }

  const filteredRooms = rooms.filter(room => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        room.room_number.toLowerCase().includes(search) ||
        room.room_type.name.toLowerCase().includes(search) ||
        (room.current_reservation && room.current_reservation.guest.name.toLowerCase().includes(search)) ||
        (room.bed_type && room.bed_type.toLowerCase().includes(search)) ||
        (room.view && room.view.toLowerCase().includes(search))
      )
    }
    return true
  })

  // Group rooms by floor
  const roomsByFloor: Record<number, Room[]> = {}
  filteredRooms.forEach(room => {
    const floor = room.floor || 0
    if (!roomsByFloor[floor]) {
      roomsByFloor[floor] = []
    }
    roomsByFloor[floor].push(room)
  })

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
                    <Home className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Room Rack</h1>
                    <p className="text-gray-600 mt-1">Real-time room status and reservation overview</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewMode(viewMode === 'rack' ? 'grid' : 'rack')}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    {viewMode === 'rack' ? 'Grid View' : 'Rack View'}
                  </button>
                  <button
                    onClick={fetchRoomRack}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                    title="Refresh"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Date Selector */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CalendarDays className="h-5 w-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">View Date:</span>
                    <button
                      onClick={() => changeDate(-1)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </button>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      className="px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                    <button
                      onClick={() => changeDate(1)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
                      className="px-3 py-1 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg"
                    >
                      Today
                    </button>
                  </div>
                </div>
              </div>

              {/* Summary Cards — solid GYOROOM status colors */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
                {statusKeys.map((status) => {
                  const config = getStatusConfig(status)
                  const count = summary[status as keyof RoomRackSummary] ?? 0
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
                        placeholder="Search by room, guest, type..."
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

            {/* Room Rack Display */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : filteredRooms.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Home className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No rooms found</h3>
                <p className="text-gray-600">Try adjusting your filters or search terms</p>
              </div>
            ) : viewMode === 'rack' ? (
              // Traditional Rack View - Organized by Floor
              <div className="space-y-6">
                {Object.keys(roomsByFloor).sort((a, b) => parseInt(b) - parseInt(a)).map(floor => (
                  <div key={floor} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                    <div className="bg-indigo-600 text-white px-6 py-3">
                      <h2 className="text-lg font-semibold">Floor {floor}</h2>
                    </div>
                    <div className="p-4">
                      <div className="flex flex-wrap gap-2 mb-3">
                        {statusKeys.map((status) => {
                          const config = getStatusConfig(status)
                          return (
                            <span key={status} className="inline-flex items-center gap-1.5 text-xs text-gray-600">
                              <span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: config.fill }} />
                              {config.label}
                            </span>
                          )
                        })}
                      </div>
                      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-2">
                        {roomsByFloor[parseInt(floor)].map((room) => {
                          const cfg = getStatusConfig(room.status)
                          const reservation = room.current_reservation

                          return (
                            <button
                              key={room.id}
                              type="button"
                              title={
                                reservation
                                  ? `${room.room_number} · ${cfg.label} · ${reservation.guest.name}`
                                  : `${room.room_number} · ${cfg.label}`
                              }
                              className={`min-h-[56px] rounded px-1 py-2 text-center text-white shadow-sm transition hover:brightness-110 ${
                                selectedRoom?.id === room.id ? 'ring-2 ring-slate-800 ring-offset-1' : ''
                              }`}
                              style={{ backgroundColor: cfg.fill }}
                              onClick={() => setSelectedRoom(room)}
                            >
                              <div className="text-sm font-bold leading-tight">{room.room_number}</div>
                              <div className="text-[10px] opacity-90 truncate">
                                {reservation ? reservation.guest.name.split(' ')[0] : cfg.label}
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              // Grid View
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredRooms.map((room) => {
                  const statusConfig = getStatusConfig(room.status)
                  const StatusIcon = statusConfig.icon
                  const reservation = room.current_reservation

                  return (
                    <div
                      key={room.id}
                      className={`bg-white border-2 ${statusConfig.borderColor} rounded-lg shadow-sm hover:shadow-lg transition-all cursor-pointer ${
                        selectedRoom?.id === room.id ? 'ring-2 ring-indigo-500' : ''
                      }`}
                      onClick={() => setSelectedRoom(room)}
                    >
                      {/* Room Header */}
                      <div className="p-4 border-b text-white" style={{ backgroundColor: statusConfig.fill }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <StatusIcon className="h-5 w-5" />
                            <span className="text-xl font-bold">{room.room_number}</span>
                            {room.floor && (
                              <span className="text-sm opacity-90">Floor {room.floor}</span>
                            )}
                          </div>
                          {reservation?.guest.is_vip && (
                            <span className="text-xs bg-yellow-400 text-yellow-900 px-2 py-1 rounded font-medium">
                              VIP
                            </span>
                          )}
                        </div>
                        <div className="text-sm font-medium opacity-95">{room.room_type.name} · {statusConfig.label}</div>
                      </div>

                      {/* Room Details */}
                      <div className="p-4 space-y-3">
                        {reservation ? (
                          <>
                            <div>
                              <div className="text-sm font-semibold text-gray-900 mb-1">
                                {reservation.guest.name}
                              </div>
                              <div className="text-xs text-gray-600 space-y-1">
                                <div className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  <span>In: {formatDate(reservation.check_in_date)}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  <span>Out: {formatDate(reservation.check_out_date)}</span>
                                </div>
                                <div className="flex items-center gap-2 mt-2">
                                  <span className="flex items-center gap-1">
                                    <Users className="h-3 w-3" />
                                    {reservation.adults + reservation.children} guests
                                  </span>
                                  <span className="text-gray-400">•</span>
                                  <span>{reservation.nights} {reservation.nights === 1 ? 'night' : 'nights'}</span>
                                </div>
                              </div>
                            </div>
                            {reservation.status === 'checked_in' && (
                              <div className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                                ✓ Checked In
                              </div>
                            )}
                            {reservation.balance && reservation.balance > 0 && (
                              <div className="text-xs text-gray-600">
                                Balance: <span className="font-medium text-red-600">{formatMoney(reservation.balance)}</span>
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-gray-500 italic text-center py-2">
                            Available
                          </div>
                        )}

                        {(room.bed_type || room.view) && (
                          <div className="pt-2 border-t border-gray-200 text-xs text-gray-600">
                            {room.bed_type && <div>Bed: {room.bed_type}</div>}
                            {room.view && <div>View: {room.view}</div>}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Room Details Modal */}
            {selectedRoom && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedRoom(null)}>
                <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                  <div className="sticky top-0 bg-indigo-600 text-white px-6 py-4 flex items-center justify-between">
                    <h3 className="text-xl font-bold">Room {selectedRoom.room_number} Details</h3>
                    <button
                      onClick={() => setSelectedRoom(null)}
                      className="text-white hover:text-gray-200"
                    >
                      <XCircle className="h-6 w-6" />
                    </button>
                  </div>
                  <div className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-600">Room Type</label>
                        <p className="text-gray-900">{selectedRoom.room_type.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Floor</label>
                        <p className="text-gray-900">{selectedRoom.floor || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Status</label>
                        <p
                          className="inline-block px-2 py-1 rounded text-sm font-semibold text-white"
                          style={{ backgroundColor: getStatusConfig(selectedRoom.status).fill }}
                        >
                          {getStatusConfig(selectedRoom.status).label}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Bed Type</label>
                        <p className="text-gray-900">{selectedRoom.bed_type || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">View</label>
                        <p className="text-gray-900">{selectedRoom.view || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Rack Rate</label>
                        <p className="text-gray-900">{selectedRoom.rack_rate == null ? 'N/A' : formatMoney(selectedRoom.rack_rate)}</p>
                      </div>
                    </div>

                    {selectedRoom.current_reservation && (
                      <div className="border-t pt-4">
                        <h4 className="font-semibold text-gray-900 mb-3">Current Reservation</h4>
                        <div className="bg-gray-200 rounded-lg p-4 space-y-3">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="text-sm font-medium text-gray-600">Reservation #</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.reservation_number}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Guest</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.guest.name}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Check-in</label>
                              <p className="text-gray-900">{formatDateTime(selectedRoom.current_reservation.check_in_date)}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Check-out</label>
                              <p className="text-gray-900">{formatDateTime(selectedRoom.current_reservation.check_out_date)}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Guests</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.adults} adults, {selectedRoom.current_reservation.children} children</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Nights</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.nights}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Rate</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.room_rate == null ? 'N/A' : formatMoney(selectedRoom.current_reservation.room_rate)}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-600">Total Amount</label>
                              <p className="text-gray-900">{selectedRoom.current_reservation.total_amount == null ? 'N/A' : formatMoney(selectedRoom.current_reservation.total_amount)}</p>
                            </div>
                            {selectedRoom.current_reservation.guest.phone && (
                              <div>
                                <label className="text-sm font-medium text-gray-600">Phone</label>
                                <p className="text-gray-900">{selectedRoom.current_reservation.guest.phone}</p>
                              </div>
                            )}
                            {selectedRoom.current_reservation.guest.email && (
                              <div>
                                <label className="text-sm font-medium text-gray-600">Email</label>
                                <p className="text-gray-900">{selectedRoom.current_reservation.guest.email}</p>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2 pt-2">
                          <button
                            type="button"
                            onClick={() => {
                              const rid = selectedRoom.current_reservation?.id
                              if (rid) router.push(`/frontdesk/reservations/${rid}`)
                            }}
                            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
                          >
                            Open folio
                          </button>
                        </div>
                      </div>
                    )}

                    {selectedRoom.all_reservations.length > 1 && (
                      <div className="border-t pt-4">
                        <h4 className="font-semibold text-gray-900 mb-3">All Reservations</h4>
                        <div className="space-y-2">
                          {selectedRoom.all_reservations.map((res) => (
                            <div key={res.id} className="bg-gray-200 rounded-lg p-3 text-sm">
                              <div className="flex justify-between">
                                <span className="font-medium">{res.guest_name}</span>
                                <span className="text-gray-600">{res.nights} nights</span>
                              </div>
                              <div className="text-gray-600 text-xs mt-1">
                                {formatDate(res.check_in_date)} - {formatDate(res.check_out_date)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Footer Stats */}
            <div className="mt-6 text-center text-sm text-gray-600">
              Showing {filteredRooms.length} of {rooms.length} rooms • Date: {formatDate(selectedDate)}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

