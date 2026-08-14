'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import { Gift, Search, Plus, RefreshCw, Calendar } from 'lucide-react'

export default function AmenityDistributionPage() {
  const router = useRouter()
  const [distributions, setDistributions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchDistributions = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/housekeeping/amenity-distribution?${params.toString()}`)
      setDistributions(response.data.items || response.data.distributions || [])
    } catch (error) {
      console.error('Error fetching amenity distributions:', error)
      setDistributions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDistributions()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchDistributions(), 300)
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
                    <Gift className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Amenity Distribution</h1>
                    <p className="text-gray-600 mt-1">Track amenity distribution to rooms</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/housekeeping/amenity-distribution/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Distribution
                  </button>
                  <button
                    onClick={fetchDistributions}
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
                    placeholder="Search by room, amenity..."
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
            ) : distributions.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Gift className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No distributions found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new distribution</p>
                <button
                  onClick={() => router.push('/housekeeping/amenity-distribution/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Distribution
                </button>
              </div>
            ) : (
              <div className="overflow-auto rounded-xl border bg-white">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-50 text-left text-slate-600">
                    <tr>
                      {['No.', 'Date', 'Room', 'Items', 'By', 'Notes'].map((h) => (
                        <th key={h} className="px-3 py-2 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {distributions.map((row: any) => (
                      <tr key={row.id} className="border-t">
                        <td className="px-3 py-2">{row.distribution_number}</td>
                        <td className="px-3 py-2">{row.distribution_date}</td>
                        <td className="px-3 py-2">{row.room_number}</td>
                        <td className="px-3 py-2">{row.items}</td>
                        <td className="px-3 py-2">{row.distributed_by}</td>
                        <td className="px-3 py-2">{row.notes || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

