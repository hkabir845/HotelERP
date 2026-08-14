'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { Users, Search, RefreshCw, User } from 'lucide-react'

export default function HousekeepingStaffPage() {
  const [staff, setStaff] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchStaff = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ department: 'housekeeping' })
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/utilities/users?${params.toString()}`)
      setStaff(response.data.users || [])
    } catch (error) {
      console.error('Error fetching staff:', error)
      setStaff([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStaff()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchStaff(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

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
                    <h1 className="text-3xl font-bold text-gray-900">Housekeeping Staff</h1>
                    <p className="text-gray-600 mt-1">Manage housekeeping staff members</p>
                  </div>
                </div>
                <button
                  onClick={fetchStaff}
                  className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by name, email..."
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
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {staff.length} staff member{staff.length !== 1 ? 's' : ''}
                </h3>
                <p className="text-gray-600">Housekeeping staff management</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

