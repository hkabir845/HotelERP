'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  Calendar,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  User,
  Home,
  DollarSign,
  RefreshCw,
  Download,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Reservation {
  id: number
  reservation_number: string
  guest: {
    id: number
    name: string
    email: string | null
    phone: string | null
    is_vip: boolean
  }
  room: {
    id: number
    room_number: string
    room_type: string
  } | null
  check_in_date: string
  check_out_date: string
  status: string
  reservation_type: string
  adults: number
  children: number
  room_rate: number
  total_amount: number
  paid_amount: number
  balance: number
  source: string | null
  nights: number
}

export default function ReservationsListPage() {
  const router = useRouter()
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    confirmed: { label: 'Confirmed', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    checked_in: { label: 'Checked In', color: 'text-green-700', bgColor: 'bg-green-100' },
    checked_out: { label: 'Checked Out', color: 'text-gray-700', bgColor: 'bg-gray-100' },
    cancelled: { label: 'Cancelled', color: 'text-red-700', bgColor: 'bg-red-100' },
    no_show: { label: 'No Show', color: 'text-orange-700', bgColor: 'bg-orange-100' }
  }

  const fetchReservations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20'
      })
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      setReservations(response.data.reservations || [])
      setTotal(response.data.total || 0)
      setTotalPages(response.data.total_pages || 1)
    } catch (error) {
      console.error('Error fetching reservations:', error)
      // Use mock data for now
      setReservations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReservations()
  }, [currentPage, statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) fetchReservations()
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
                    <Calendar className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Reservation List</h1>
                    <p className="text-gray-600 mt-1">View and manage all reservations</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/frontdesk/reservations/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Reservation
                  </button>
                  <button
                    onClick={fetchReservations}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
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
                        placeholder="Search by reservation #, guest name, room..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <select
                    value={statusFilter}
                    onChange={(e) => {
                      setStatusFilter(e.target.value)
                      setCurrentPage(1)
                    }}
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

            {/* Reservations Table */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : reservations.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No reservations found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new reservation</p>
                <button
                  onClick={() => router.push('/frontdesk/reservations/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Reservation
                </button>
              </div>
            ) : (
              <>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Reservation #
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Guest
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Room
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Check-in
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Check-out
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Nights
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Total
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Balance
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {reservations.map((reservation) => {
                          const status = statusConfig[reservation.status] || statusConfig.pending
                          return (
                            <tr key={reservation.id} className="hover:bg-gray-200">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">
                                  {reservation.reservation_number}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {reservation.reservation_type}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <div>
                                    <div className="text-sm font-medium text-gray-900">
                                      {reservation.guest.name}
                                      {reservation.guest.is_vip && (
                                        <span className="ml-2 text-xs bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded">
                                          VIP
                                        </span>
                                      )}
                                    </div>
                                    {reservation.guest.phone && (
                                      <div className="text-sm text-gray-500">{reservation.guest.phone}</div>
                                    )}
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                {reservation.room ? (
                                  <div>
                                    <div className="text-sm font-medium text-gray-900">
                                      {reservation.room.room_number}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {reservation.room.room_type}
                                    </div>
                                  </div>
                                ) : (
                                  <span className="text-sm text-gray-400">Not assigned</span>
                                )}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {formatDate(reservation.check_in_date)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {formatDate(reservation.check_out_date)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {reservation.nights}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                                  {status.label}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {formatMoney(reservation.total_amount)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`text-sm font-medium ${reservation.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                  {formatMoney(reservation.balance)}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <div className="flex items-center justify-end gap-2">
                                  <button
                                    onClick={() => router.push(`/frontdesk/reservations/${reservation.id}`)}
                                    className="text-indigo-600 hover:text-indigo-900"
                                    title="Folio"
                                  >
                                    <Eye className="h-4 w-4" />
                                  </button>
                                  {(reservation.status === 'confirmed' || reservation.status === 'pending') && (
                                    <button
                                      onClick={async () => {
                                        try {
                                          await apiClient.post(`/reservations/${reservation.id}/check-in`)
                                          fetchReservations()
                                        } catch (err: any) {
                                          alert(err.response?.data?.detail || 'Check-in failed')
                                        }
                                      }}
                                      className="text-green-700 hover:underline text-xs"
                                    >
                                      Check in
                                    </button>
                                  )}
                                  {reservation.status === 'checked_in' && (
                                    <button
                                      onClick={() => router.push(`/frontdesk/reservations/${reservation.id}`)}
                                      className="text-orange-700 hover:underline text-xs"
                                    >
                                      Check out
                                    </button>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                      Showing {(currentPage - 1) * 20 + 1} to {Math.min(currentPage * 20, total)} of {total} reservations
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </button>
                      <span className="text-sm text-gray-700">
                        Page {currentPage} of {totalPages}
                      </span>
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

