'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  UserPlus,
  Search,
  Plus,
  RefreshCw,
  Eye,
  Calendar,
  User,
  Home
} from 'lucide-react'

interface Registration {
  id: number
  registration_number: string
  guest: {
    name: string
    email: string | null
    phone: string | null
  }
  room: {
    room_number: string
    room_type: string
  } | null
  check_in_date: string
  check_out_date: string
  status: string
  adults: number
  children: number
}

export default function RegistrationsListPage() {
  const router = useRouter()
  const [registrations, setRegistrations] = useState<Registration[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchRegistrations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ reservation_type: 'walk_in' })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/reservations?${params.toString()}`)
      setRegistrations(response.data.reservations || [])
    } catch (error) {
      console.error('Error fetching registrations:', error)
      setRegistrations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRegistrations()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchRegistrations(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
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
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <UserPlus className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Registrations</h1>
                    <p className="text-gray-600 mt-1">Walk-in guest registrations</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/frontdesk/registrations/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Registration
                  </button>
                  <button
                    onClick={fetchRegistrations}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by guest name, registration #..."
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
            ) : registrations.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <UserPlus className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No registrations found</h3>
                <p className="text-gray-600">Get started by creating a new registration</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Registration #</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-in</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-out</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guests</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {registrations.map((reg) => (
                        <tr key={reg.id} className="hover:bg-gray-200">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {reg.registration_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{reg.guest.name}</div>
                            {reg.guest.phone && <div className="text-sm text-gray-500">{reg.guest.phone}</div>}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {reg.room ? (
                              <div>
                                <div className="text-sm font-medium text-gray-900">{reg.room.room_number}</div>
                                <div className="text-sm text-gray-500">{reg.room.room_type}</div>
                              </div>
                            ) : (
                              <span className="text-sm text-gray-400">Not assigned</span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(reg.check_in_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(reg.check_out_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {reg.adults + reg.children} ({reg.adults}A, {reg.children}C)
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              reg.status === 'checked_in' ? 'bg-green-100 text-green-700' :
                              reg.status === 'confirmed' ? 'bg-blue-100 text-blue-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>
                              {reg.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => router.push(`/frontdesk/reservations/${reg.id}`)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              <Eye className="h-4 w-4" />
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

