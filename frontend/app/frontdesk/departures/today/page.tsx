'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  Calendar,
  Search,
  User,
  Home,
  Phone,
  RefreshCw,
  LogOut,
  AlertCircle
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Departure {
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
  actual_check_out: string | null
  status: string
  adults: number
  children: number
  total_amount: number
  paid_amount: number
  balance: number
}

export default function DeparturesTodayPage() {
  const router = useRouter()
  const [departures, setDepartures] = useState<Departure[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchDepartures = async () => {
    try {
      setLoading(true)
      const today = new Date().toISOString().split('T')[0]
      const params = new URLSearchParams({
        check_out_date: today
      })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      // Filter for checked-in or confirmed reservations
      const filtered = (response.data.reservations || []).filter(
        (r: any) => r.status === 'checked_in' || r.status === 'confirmed'
      )
      setDepartures(filtered)
    } catch (error) {
      console.error('Error fetching departures:', error)
      setDepartures([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDepartures()
    const interval = setInterval(fetchDepartures, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchDepartures(), 300)
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

  const pendingCheckouts = departures.filter(d => !d.actual_check_out && d.balance > 0)
  const totalOutstanding = departures.reduce((sum, d) => sum + d.balance, 0)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <LogOut className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Today's Departures</h1>
                    <p className="text-gray-600 mt-1">Guests departing today - {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                </div>
                <button
                  onClick={fetchDepartures}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Departures</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{departures.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Pending Checkouts</div>
                  <div className="text-2xl font-bold text-orange-600 mt-1">{pendingCheckouts.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Outstanding Balance</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{formatMoney(totalOutstanding)}</div>
                </div>
              </div>

              {pendingCheckouts.length > 0 && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-orange-600" />
                    <span className="font-medium text-orange-900">
                      {pendingCheckouts.length} guest{pendingCheckouts.length !== 1 ? 's' : ''} with outstanding balance need to checkout
                    </span>
                  </div>
                </div>
              )}

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
            ) : departures.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <LogOut className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No departures today</h3>
                <p className="text-gray-600">No guests are scheduled to depart today</p>
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
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {departures.map((departure) => (
                        <tr key={departure.id} className={departure.balance > 0 ? 'bg-orange-50' : 'hover:bg-gray-200'}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {departure.room ? (
                              <div>
                                <div className="text-sm font-medium text-gray-900">{departure.room.room_number}</div>
                                <div className="text-sm text-gray-500">{departure.room.room_type}</div>
                              </div>
                            ) : (
                              <span className="text-sm text-gray-400">Not assigned</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm font-medium text-gray-900">
                              {departure.guest.name}
                              {departure.guest.is_vip && (
                                <span className="ml-2 text-xs bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded">VIP</span>
                              )}
                            </div>
                            {departure.guest.phone && (
                              <div className="text-sm text-gray-500">{departure.guest.phone}</div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(departure.check_in_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(departure.check_out_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {departure.actual_check_out ? (
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                                Checked Out
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-700">
                                Pending
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatMoney(departure.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`text-sm font-medium ${departure.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {formatMoney(departure.balance)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <button
                              type="button"
                              onClick={() => router.push(`/frontdesk/reservations/${departure.id}`)}
                              className="text-indigo-700 hover:underline"
                            >
                              Folio
                            </button>
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

