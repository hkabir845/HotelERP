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
  Mail,
  Clock,
  RefreshCw,
  CheckCircle2
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Arrival {
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
  adults: number
  children: number
  total_amount: number
  paid_amount: number
  balance: number
  source: string | null
}

export default function ArrivalsTodayPage() {
  const router = useRouter()
  const [arrivals, setArrivals] = useState<Arrival[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchArrivals = async () => {
    try {
      setLoading(true)
      const today = new Date().toISOString().split('T')[0]
      const params = new URLSearchParams({
        status: 'confirmed',
        check_in_date: today
      })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      setArrivals(response.data.reservations || [])
    } catch (error) {
      console.error('Error fetching arrivals:', error)
      setArrivals([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArrivals()
    const interval = setInterval(fetchArrivals, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchArrivals(), 300)
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

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Calendar className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Today's Arrivals</h1>
                    <p className="text-gray-600 mt-1">Guests arriving today - {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                </div>
                <button
                  onClick={fetchArrivals}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              {/* Summary */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-green-900">
                    {arrivals.length} guest{arrivals.length !== 1 ? 's' : ''} arriving today
                  </span>
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
            ) : arrivals.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No arrivals today</h3>
                <p className="text-gray-600">No guests are scheduled to arrive today</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {arrivals.map((arrival) => (
                  <div key={arrival.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="text-sm font-medium text-gray-500">Reservation #</div>
                        <div className="text-lg font-bold text-gray-900">{arrival.reservation_number}</div>
                      </div>
                      {arrival.guest.is_vip && (
                        <span className="text-xs bg-yellow-400 text-yellow-900 px-2 py-1 rounded font-medium">
                          VIP
                        </span>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-gray-600">Guest</div>
                        <div className="text-base font-medium text-gray-900">{arrival.guest.name}</div>
                        {arrival.guest.phone && (
                          <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                            <Phone className="h-3 w-3" />
                            {arrival.guest.phone}
                          </div>
                        )}
                      </div>

                      {arrival.room && (
                        <div>
                          <div className="text-sm text-gray-600">Room</div>
                          <div className="text-base font-medium text-gray-900">
                            {arrival.room.room_number} - {arrival.room.room_type}
                          </div>
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
                        <div>
                          <div className="text-sm text-gray-600">Check-in</div>
                          <div className="text-sm font-medium text-gray-900">{formatDate(arrival.check_in_date)}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Check-out</div>
                          <div className="text-sm font-medium text-gray-900">{formatDate(arrival.check_out_date)}</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
                        <div>
                          <div className="text-sm text-gray-600">Guests</div>
                          <div className="text-sm font-medium text-gray-900">
                            {arrival.adults + arrival.children} ({arrival.adults}A, {arrival.children}C)
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Balance</div>
                          <div className={`text-sm font-medium ${arrival.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {formatMoney(arrival.balance)}
                          </div>
                        </div>
                      </div>

                      {arrival.source && (
                        <div className="pt-3 border-t border-gray-200">
                          <div className="text-sm text-gray-600">Source</div>
                          <div className="text-sm font-medium text-gray-900">{arrival.source}</div>
                        </div>
                      )}
                      <div className="flex gap-2 pt-3 border-t border-gray-200">
                        <button
                          type="button"
                          onClick={() => router.push(`/frontdesk/reservations/${arrival.id}`)}
                          className="flex-1 rounded-lg border px-3 py-2 text-sm"
                        >
                          Folio
                        </button>
                        {arrival.status !== 'checked_in' && arrival.status !== 'checked_out' && (
                          <button
                            type="button"
                            onClick={async () => {
                              try {
                                await apiClient.post(`/reservations/${arrival.id}/check-in`)
                                fetchArrivals()
                              } catch (err: any) {
                                alert(err.response?.data?.detail || 'Check-in failed')
                              }
                            }}
                            className="flex-1 rounded-lg bg-green-600 px-3 py-2 text-sm text-white"
                          >
                            Check in
                          </button>
                        )}
                      </div>
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

