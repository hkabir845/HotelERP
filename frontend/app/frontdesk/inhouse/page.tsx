'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  Users,
  Search,
  Home,
  Calendar,
  Phone,
  Mail,
  DollarSign,
  RefreshCw,
  Eye,
  LogOut as CheckOutIcon
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface InhouseGuest {
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
    floor: number | null
  } | null
  check_in_date: string
  check_out_date: string
  actual_check_in: string | null
  adults: number
  children: number
  total_amount: number
  paid_amount: number
  balance: number
  nights: number
}

export default function InhousePage() {
  const router = useRouter()
  const [guests, setGuests] = useState<InhouseGuest[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchInhouseGuests = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ status: 'checked_in' })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      setGuests(response.data.reservations || [])
    } catch (error) {
      console.error('Error fetching inhouse guests:', error)
      setGuests([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInhouseGuests()
    const interval = setInterval(fetchInhouseGuests, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchInhouseGuests(), 300)
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

  const totalRevenue = guests.reduce((sum, g) => sum + g.total_amount, 0)
  const totalBalance = guests.reduce((sum, g) => sum + g.balance, 0)

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
                    <Users className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Inhouse Guests</h1>
                    <p className="text-gray-600 mt-1">Currently checked-in guests</p>
                  </div>
                </div>
                <button
                  onClick={fetchInhouseGuests}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Inhouse</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{guests.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Revenue</div>
                  <div className="text-2xl font-bold text-indigo-600 mt-1">{formatMoney(totalRevenue)}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Outstanding Balance</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{formatMoney(totalBalance)}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">VIP Guests</div>
                  <div className="text-2xl font-bold text-yellow-600 mt-1">
                    {guests.filter(g => g.guest.is_vip).length}
                  </div>
                </div>
              </div>

              {/* Search */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by guest name, room number, reservation #..."
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
            ) : guests.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No inhouse guests</h3>
                <p className="text-gray-600">No guests are currently checked in</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-in</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-out</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nights</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {guests.map((guest) => (
                        <tr key={guest.id} className="hover:bg-gray-200">
                          <td className="px-6 py-4 whitespace-nowrap">
                            {guest.room ? (
                              <div>
                                <div className="text-sm font-medium text-gray-900">{guest.room.room_number}</div>
                                <div className="text-sm text-gray-500">{guest.room.room_type}</div>
                              </div>
                            ) : (
                              <span className="text-sm text-gray-400">Not assigned</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm font-medium text-gray-900">
                              {guest.guest.name}
                              {guest.guest.is_vip && (
                                <span className="ml-2 text-xs bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded">VIP</span>
                              )}
                            </div>
                            {guest.guest.phone && (
                              <div className="text-sm text-gray-500">{guest.guest.phone}</div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(guest.actual_check_in || guest.check_in_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(guest.check_out_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {guest.nights}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatMoney(guest.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`text-sm font-medium ${guest.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {formatMoney(guest.balance)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => router.push(`/frontdesk/reservations/${guest.id}`)}
                                className="text-indigo-600 hover:text-indigo-900"
                                title="Folio"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => router.push(`/frontdesk/reservations/${guest.id}`)}
                                className="text-orange-700 hover:underline text-xs"
                              >
                                Check out
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
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

