'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  FileText,
  Search,
  RefreshCw,
  DollarSign,
  AlertCircle,
  User,
  Home,
  Calendar
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface PendingFolio {
  id: number
  reservation_number: string
  guest: {
    name: string
    phone: string | null
  }
  room: {
    room_number: string
  } | null
  total_amount: number
  paid_amount: number
  balance: number
  check_out_date: string
  days_overdue: number
}

export default function PendingFolioPage() {
  const [folios, setFolios] = useState<PendingFolio[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchPendingFolios = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ status: 'checked_in' })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      const reservations = response.data.reservations || []
      
      // Filter for those with outstanding balance
      const pending = reservations
        .filter((r: any) => r.balance > 0)
        .map((r: any) => {
          const checkOut = new Date(r.check_out_date)
          const today = new Date()
          const daysOverdue = Math.max(0, Math.floor((today.getTime() - checkOut.getTime()) / (1000 * 60 * 60 * 24)))
          
          return {
            id: r.id,
            reservation_number: r.reservation_number,
            guest: r.guest,
            room: r.room,
            total_amount: r.total_amount,
            paid_amount: r.paid_amount,
            balance: r.balance,
            check_out_date: r.check_out_date,
            days_overdue: daysOverdue
          }
        })
      
      setFolios(pending)
    } catch (error) {
      console.error('Error fetching pending folios:', error)
      setFolios([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPendingFolios()
    const interval = setInterval(fetchPendingFolios, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchPendingFolios(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const totalOutstanding = folios.reduce((sum, f) => sum + f.balance, 0)
  const overdueCount = folios.filter(f => f.days_overdue > 0).length

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <FileText className="h-6 w-6 text-red-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Pending Folio</h1>
                    <p className="text-gray-600 mt-1">Outstanding balances requiring attention</p>
                  </div>
                </div>
                <button
                  onClick={fetchPendingFolios}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Pending</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{folios.length}</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Total Outstanding</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{formatMoney(totalOutstanding)}</div>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Overdue</div>
                  <div className="text-2xl font-bold text-orange-600 mt-1">{overdueCount}</div>
                </div>
              </div>

              {overdueCount > 0 && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-orange-600" />
                    <span className="font-medium text-orange-900">
                      {overdueCount} folio{overdueCount !== 1 ? 's' : ''} {overdueCount === 1 ? 'is' : 'are'} overdue
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
                    placeholder="Search by guest name, reservation #, room..."
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
            ) : folios.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No pending folios</h3>
                <p className="text-gray-600">All folios have been settled</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reservation #</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-out</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paid</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {folios.map((folio) => (
                        <tr key={folio.id} className={folio.days_overdue > 0 ? 'bg-orange-50' : 'hover:bg-gray-200'}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {folio.reservation_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{folio.guest.name}</div>
                            {folio.guest.phone && <div className="text-sm text-gray-500">{folio.guest.phone}</div>}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {folio.room ? (
                              <div className="text-sm font-medium text-gray-900">{folio.room.room_number}</div>
                            ) : (
                              <span className="text-sm text-gray-400">Not assigned</span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(folio.check_out_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatMoney(folio.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatMoney(folio.paid_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm font-bold text-red-600">
                              {formatMoney(folio.balance)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {folio.days_overdue > 0 ? (
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-700">
                                {folio.days_overdue} day{folio.days_overdue !== 1 ? 's' : ''} overdue
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">
                                Pending
                              </span>
                            )}
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

