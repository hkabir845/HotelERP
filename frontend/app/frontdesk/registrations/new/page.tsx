'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  UserPlus,
  User,
  Home,
  Calendar,
  Save,
  Loader2,
  CheckCircle2,
  Search
} from 'lucide-react'

interface Guest {
  id: number
  name: string
  email: string | null
  phone: string | null
  is_vip: boolean
}

export default function NewRegistrationPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState<Guest[]>([])
  const [selectedGuest, setSelectedGuest] = useState<Guest | null>(null)
  const [roomNumber, setRoomNumber] = useState('')
  const [checkInDate, setCheckInDate] = useState(new Date().toISOString().split('T')[0])
  const [checkOutDate, setCheckOutDate] = useState(new Date(Date.now() + 86400000).toISOString().split('T')[0])
  const [adults, setAdults] = useState(1)
  const [children, setChildren] = useState(0)
  const [notes, setNotes] = useState('')
  const [success, setSuccess] = useState(false)

  const searchGuests = async (query: string) => {
    if (query.length < 2) {
      setSearchResults([])
      return
    }

    try {
      const response = await apiClient.get(`/reservations/guests/search?query=${encodeURIComponent(query)}`)
      setSearchResults(response.data.guests || [])
    } catch (error) {
      console.error('Error searching guests:', error)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm) searchGuests(searchTerm)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedGuest) return

    setSubmitting(true)
    try {
      // Create registration (similar to reservation but for walk-in)
      const payload = {
        guest_id: selectedGuest.id,
        check_in_date: checkInDate + 'T14:00:00',
        check_out_date: checkOutDate + 'T11:00:00',
        reservation_type: 'walk_in',
        status: 'confirmed',
        adults,
        children,
        room_rate: 100, // Default rate
        paid_amount: 0,
        source: 'Walk-in',
        notes
      }

      await apiClient.post('/reservations/create', payload)
      setSuccess(true)
      setTimeout(() => router.push('/frontdesk/registrations'), 2000)
    } catch (error: any) {
      console.error('Error creating registration:', error)
      alert(error.response?.data?.detail || 'Failed to create registration')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <UserPlus className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">New Registration</h1>
                  <p className="text-gray-600 mt-1">Register a walk-in guest</p>
                </div>
              </div>
            </div>

            {success && (
              <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <p className="font-medium text-green-900">Registration created successfully!</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="max-w-2xl">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search Guest <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value)
                        setSelectedGuest(null)
                      }}
                      placeholder="Search by name, email, or phone..."
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                    {searchResults.length > 0 && !selectedGuest && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {searchResults.map((guest) => (
                          <div
                            key={guest.id}
                            onClick={() => {
                              setSelectedGuest(guest)
                              setSearchTerm(guest.name)
                              setSearchResults([])
                            }}
                            className="p-3 hover:bg-gray-200 cursor-pointer border-b border-gray-100 last:border-b-0"
                          >
                            <div className="font-medium text-gray-900">{guest.name}</div>
                            {guest.email && <div className="text-sm text-gray-600">{guest.email}</div>}
                            {guest.phone && <div className="text-sm text-gray-600">{guest.phone}</div>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  {selectedGuest && (
                    <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{selectedGuest.name}</div>
                          {selectedGuest.email && <div className="text-sm text-gray-600">{selectedGuest.email}</div>}
                        </div>
                        {selectedGuest.is_vip && (
                          <span className="text-xs bg-yellow-400 text-yellow-900 px-2 py-1 rounded">VIP</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Check-in Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={checkInDate}
                      onChange={(e) => setCheckInDate(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Check-out Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={checkOutDate}
                      onChange={(e) => setCheckOutDate(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Adults <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={adults}
                      onChange={(e) => setAdults(parseInt(e.target.value) || 1)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Children
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={children}
                      onChange={(e) => setChildren(parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="Additional notes..."
                  />
                </div>

                <div className="flex items-center justify-end gap-4 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => router.back()}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || !selectedGuest}
                    className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        Create Registration
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

