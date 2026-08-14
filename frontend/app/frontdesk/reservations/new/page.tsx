'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  Calendar,
  User,
  Home,
  Users,
  DollarSign,
  Search,
  Plus,
  X,
  Save,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Info,
  CreditCard,
  Phone,
  Mail,
  MapPin,
  CalendarDays,
  Bed,
  Clock,
  ChevronDown,
  Upload,
  FileText
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Guest {
  id: number
  name: string
  email: string | null
  phone: string | null
  is_vip: boolean
  loyalty_points: number
}

interface RoomType {
  id: number
  name: string
  base_rate: number | null
  max_occupancy: number
}

interface Room {
  id: number
  room_number: string
  floor: number | null
  room_type: {
    id: number
    name: string
    base_rate: number | null
  }
  rack_rate: number | null
  bed_type: string | null
  view: string | null
}

interface FormData {
  // Guest
  guest_id: number | null
  guest_search: string
  use_existing_guest: boolean
  guest: {
    title: string
    first_name: string
    last_name: string
    email: string
    phone: string
    mobile: string
    country_code: string
    gender: string
    date_of_birth: string
    profession: string
    father_husband: string
    company: string
    address_line1: string
    city: string
    state: string
    country: string
    postal_code: string
    id_type: string
    id_number: string
    id_image: File | null
    nationality: string
    is_vip: boolean
    source: string
    comments: string
  }
  
  // Booking
  walk_in_guest: boolean
  check_in_date: string
  check_out_date: string
  nights: number
  booking_type: string
  day_use: string
  board_type: string
  rooms_count: number
  
  // Room
  rooms: Array<{
    room_id: number | null
    room_type_id: number | null
    adults: number
    children: number
    extra_bed: string
    extra_bed_charge: number
    room_rate: number
    service_charge: number
    vat: number
    sub_total: number
    total_rent: number
  }>
  
  // Reservation
  reservation_type: string
  status: string
  
  // Pricing
  total_amount: number
  paid_amount: number
  
  // Additional
  booking_agent: string
  special_requests: string
  notes: string
  sharers: Array<{ name: string; relation: string; id_number: string }>
  pickup: {
    pickup_required: boolean
    pickup_from: string
    pickup_time: string
    drop_required: boolean
    drop_to: string
    drop_time: string
    vehicle: string
    notes: string
  }
  complimentaries: Array<{ item: string; quantity: number; notes: string }>
}

export default function NewReservationPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState('reservation')
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([])
  const [availableRooms, setAvailableRooms] = useState<Room[]>([])
  const [boardTypes, setBoardTypes] = useState<{ id: number; name: string }[]>([])
  const [guestSources, setGuestSources] = useState<{ id: number; name: string }[]>([])
  const [compOptions, setCompOptions] = useState<{ id: number; name: string }[]>([])
  const [searchResults, setSearchResults] = useState<Guest[]>([])
  const [showGuestSearch, setShowGuestSearch] = useState(false)
  const [calculating, setCalculating] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [success, setSuccess] = useState(false)
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)

  const [formData, setFormData] = useState<FormData>({
    guest_id: null,
    guest_search: '',
    use_existing_guest: false,
    guest: {
      title: 'Mr',
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      mobile: '',
      country_code: '+880',
      gender: 'Male',
      date_of_birth: '',
      profession: '',
      father_husband: '',
      company: '',
      address_line1: '',
      city: '',
      state: '',
      country: 'Bangladesh',
      postal_code: '',
      id_type: '',
      id_number: '',
      id_image: null,
      nationality: 'Bangladesh',
      is_vip: false,
      source: '',
      comments: ''
    },
    walk_in_guest: false,
    check_in_date: new Date().toISOString().split('T')[0],
    check_out_date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
    nights: 1,
    booking_type: 'Confirm',
    day_use: 'No',
    board_type: 'Room Only',
    rooms_count: 1,
    rooms: [{
      room_id: null,
      room_type_id: null,
      adults: 1,
      children: 0,
      extra_bed: 'No',
      extra_bed_charge: 0,
      room_rate: 0,
      service_charge: 0,
      vat: 0,
      sub_total: 0,
      total_rent: 0
    }],
    reservation_type: 'individual',
    status: 'confirmed',
    total_amount: 0,
    paid_amount: 0,
    booking_agent: '',
    special_requests: '',
    notes: '',
    sharers: [{ name: '', relation: '', id_number: '' }],
    pickup: {
      pickup_required: false,
      pickup_from: '',
      pickup_time: '',
      drop_required: false,
      drop_to: '',
      drop_time: '',
      vehicle: '',
      notes: ''
    },
    complimentaries: [{ item: '', quantity: 1, notes: '' }]
  })

  useEffect(() => {
    fetchRoomTypes()
  }, [])

  useEffect(() => {
    if (formData.check_in_date && formData.check_out_date) {
      const checkIn = new Date(formData.check_in_date)
      const checkOut = new Date(formData.check_out_date)
      const nights = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24))
      setFormData(prev => ({ ...prev, nights: nights > 0 ? nights : 1 }))
      checkRoomAvailability()
    }
  }, [formData.check_in_date, formData.check_out_date])

  useEffect(() => {
    calculateRoomTotals()
  }, [formData.rooms, formData.nights])

  const fetchRoomTypes = async () => {
    try {
      const [types, boards, sources, comps] = await Promise.all([
        apiClient.get('/frontdesk/room-rack/types'),
        apiClient.get('/frontdesk/config/board-types'),
        apiClient.get('/frontdesk/config/guest-sources'),
        apiClient.get('/frontdesk/config/complimentary-options'),
      ])
      setRoomTypes(types.data.room_types || [])
      setBoardTypes((boards.data.items || []).filter((row: any) => row.is_active !== false))
      setGuestSources((sources.data.items || []).filter((row: any) => row.is_active !== false))
      setCompOptions((comps.data.items || []).filter((row: any) => row.is_active !== false))
    } catch (error) {
      console.error('Error fetching room types:', error)
    }
  }

  const checkRoomAvailability = async () => {
    if (!formData.check_in_date || !formData.check_out_date) return

    try {
      setCalculating(true)
      const params = new URLSearchParams({
        check_in: formData.check_in_date,
        check_out: formData.check_out_date
      })

      const response = await apiClient.get(`/reservations/rooms/available?${params.toString()}`)
      setAvailableRooms(response.data.rooms || [])
    } catch (error) {
      console.error('Error checking availability:', error)
    } finally {
      setCalculating(false)
    }
  }

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

  const selectGuest = (guest: Guest) => {
    setFormData(prev => ({
      ...prev,
      guest_id: guest.id,
      use_existing_guest: true,
      guest_search: guest.name
    }))
    setSearchResults([])
    setShowGuestSearch(false)
  }

  const calculateRoomTotals = () => {
    const updatedRooms = formData.rooms.map(room => {
      const roomRate = room.room_rate || 0
      const serviceCharge = room.service_charge || 0
      const vat = room.vat || 0
      const subTotal = (roomRate + serviceCharge + vat) * formData.nights
      const totalRent = subTotal + (room.extra_bed === 'Yes' ? room.extra_bed_charge : 0)
      
      return {
        ...room,
        sub_total: subTotal,
        total_rent: totalRent
      }
    })

    const totalAmount = updatedRooms.reduce((sum, room) => sum + room.total_rent, 0)
    
    setFormData(prev => ({
      ...prev,
      rooms: updatedRooms,
      total_amount: totalAmount
    }))
  }

  const addRoom = () => {
    setFormData(prev => ({
      ...prev,
      rooms_count: prev.rooms_count + 1,
      rooms: [...prev.rooms, {
        room_id: null,
        room_type_id: null,
        adults: 1,
        children: 0,
        extra_bed: 'No',
        extra_bed_charge: 0,
        room_rate: 0,
        service_charge: 0,
        vat: 0,
        sub_total: 0,
        total_rent: 0
      }]
    }))
  }

  const removeRoom = (index: number) => {
    if (formData.rooms.length > 1) {
      setFormData(prev => ({
        ...prev,
        rooms_count: prev.rooms_count - 1,
        rooms: prev.rooms.filter((_, i) => i !== index)
      }))
    }
  }

  const updateRoom = (index: number, field: string, value: any) => {
    setFormData(prev => {
      const updatedRooms = [...prev.rooms]
      updatedRooms[index] = { ...updatedRooms[index], [field]: value }
      
      // Auto-set room rate when room is selected
      if (field === 'room_id' && value) {
        const room = availableRooms.find(r => r.id === value)
        if (room) {
          updatedRooms[index].room_rate = room.rack_rate || room.room_type.base_rate || 0
        }
      }
      
      return { ...prev, rooms: updatedRooms }
    })
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.use_existing_guest) {
      if (!formData.guest.first_name) newErrors['guest.first_name'] = 'First name is required'
      if (!formData.guest.last_name) newErrors['guest.last_name'] = 'Last name is required'
      if (!formData.guest.mobile) newErrors['guest.mobile'] = 'Mobile number is required'
    } else if (!formData.guest_id) {
      newErrors['guest_id'] = 'Please select a guest'
    }

    if (!formData.check_in_date) newErrors['check_in_date'] = 'Check-in date is required'
    if (!formData.check_out_date) newErrors['check_out_date'] = 'Check-out date is required'
    
    if (formData.check_in_date && formData.check_out_date) {
      const checkIn = new Date(formData.check_in_date)
      const checkOut = new Date(formData.check_out_date)
      if (checkOut <= checkIn) {
        newErrors['check_out_date'] = 'Check-out must be after check-in'
      }
    }

    formData.rooms.forEach((room, index) => {
      if (!room.room_type_id && !room.room_id) {
        newErrors[`room_${index}`] = 'Please select a room type or specific room'
      }
      if (!room.room_rate || room.room_rate <= 0) {
        newErrors[`room_rate_${index}`] = 'Room rate is required'
      }
      if (room.adults < 1) {
        newErrors[`adults_${index}`] = 'At least 1 adult is required'
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setSubmitting(true)
    setSuccess(false)

    try {
      // For now, submit first room only (can be extended for multiple rooms)
      const firstRoom = formData.rooms[0]
      const payload: any = {
        guest_id: formData.use_existing_guest ? formData.guest_id : null,
        guest: formData.use_existing_guest ? undefined : {
          title: formData.guest.title,
          first_name: formData.guest.first_name,
          last_name: formData.guest.last_name,
          email: formData.guest.email,
          phone: formData.guest.phone || formData.guest.mobile,
          mobile: formData.guest.mobile,
          country_code: formData.guest.country_code,
          gender: formData.guest.gender,
          date_of_birth: formData.guest.date_of_birth,
          profession: formData.guest.profession,
          father_husband: formData.guest.father_husband,
          company: formData.guest.company,
          address_line1: formData.guest.address_line1,
          city: formData.guest.city,
          state: formData.guest.state,
          country: formData.guest.country,
          postal_code: formData.guest.postal_code,
          id_type: formData.guest.id_type,
          id_number: formData.guest.id_number,
          nationality: formData.guest.nationality,
          is_vip: formData.guest.is_vip
        },
        room_id: firstRoom.room_id,
        room_type_id: firstRoom.room_type_id,
        check_in_date: formData.check_in_date + 'T14:00:00',
        check_out_date: formData.check_out_date + 'T11:00:00',
        reservation_type: formData.reservation_type,
        status: formData.status,
        adults: firstRoom.adults,
        children: firstRoom.children,
        room_rate: firstRoom.room_rate,
        total_amount: formData.total_amount,
        paid_amount: formData.paid_amount,
        source: formData.guest.source || null,
        booking_agent: formData.booking_agent || null,
        board_type: formData.board_type || null,
        special_requests: formData.special_requests || null,
        notes: [
          formData.notes,
          formData.guest.comments,
          formData.sharers.filter((s) => s.name.trim()).length
            ? 'Sharers: ' + formData.sharers.filter((s) => s.name.trim()).map((s) => `${s.name}${s.relation ? ` (${s.relation})` : ''}${s.id_number ? ` ID:${s.id_number}` : ''}`).join('; ')
            : '',
          formData.board_type ? `Board: ${formData.board_type}` : '',
          formData.pickup.pickup_required || formData.pickup.drop_required
            ? `Transport: pickup=${formData.pickup.pickup_required ? `${formData.pickup.pickup_from} ${formData.pickup.pickup_time}` : 'no'}; drop=${formData.pickup.drop_required ? `${formData.pickup.drop_to} ${formData.pickup.drop_time}` : 'no'}; vehicle=${formData.pickup.vehicle || '-'}`
            : '',
          formData.complimentaries.filter((c) => c.item.trim()).length
            ? 'Complimentaries: ' + formData.complimentaries.filter((c) => c.item.trim()).map((c) => `${c.item} x${c.quantity}`).join('; ')
            : '',
        ].filter(Boolean).join('\n') || null
      }

      const response = await apiClient.post('/reservations/create', payload)
      
      setSuccess(true)
      setTimeout(() => {
        router.push('/frontdesk/reservations')
      }, 2000)
    } catch (error: any) {
      console.error('Error creating reservation:', error)
      setErrors({
        submit: error.response?.data?.detail || 'Failed to create reservation. Please try again.'
      })
    } finally {
      setSubmitting(false)
    }
  }

  const tabs = [
    { id: 'reservation', label: 'Reservation Info' },
    { id: 'sharer', label: 'Sharer Info' },
    { id: 'pickup', label: 'Pickup/Drop' },
    { id: 'complimentaries', label: 'Complimentaries' }
  ]

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">New Reservation</h1>
                  <p className="text-gray-600 mt-1">Create a new reservation for a guest</p>
                </div>
              </div>
            </div>

            {success && (
              <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">Reservation created successfully!</p>
                  <p className="text-sm text-green-700">Redirecting to reservations list...</p>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
              <div className="flex border-b border-gray-200">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? 'border-indigo-600 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {activeTab === 'reservation' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Left Column - Booking Details */}
                  <div className="space-y-6">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-900">Booking Details</h2>
                        <button
                          type="button"
                          onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                          className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                        >
                          Advanced Options
                          <ChevronDown className={`h-4 w-4 transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`} />
                        </button>
                      </div>

                      {showAdvancedOptions && (
                        <div className="mb-4 p-3 bg-gray-200 rounded-lg">
                          <label className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.walk_in_guest}
                              onChange={(e) => setFormData(prev => ({ ...prev, walk_in_guest: e.target.checked }))}
                              className="rounded"
                            />
                            <span className="text-sm font-medium text-gray-700">Walk In Guest</span>
                          </label>
                        </div>
                      )}

                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Check in Date <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="date"
                            value={formData.check_in_date}
                            onChange={(e) => setFormData(prev => ({ ...prev, check_in_date: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          />
                          {errors.check_in_date && (
                            <p className="mt-1 text-sm text-red-600">{errors.check_in_date}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Night</label>
                          <input
                            type="number"
                            value={formData.nights}
                            readOnly
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-200"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Check out Date <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="date"
                            value={formData.check_out_date}
                            onChange={(e) => setFormData(prev => ({ ...prev, check_out_date: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          />
                          {errors.check_out_date && (
                            <p className="mt-1 text-sm text-red-600">{errors.check_out_date}</p>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Booking Type <span className="text-red-500">*</span>
                          </label>
                          <select
                            value={formData.booking_type}
                            onChange={(e) => setFormData(prev => ({ ...prev, booking_type: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          >
                            <option value="Confirm">Confirm</option>
                            <option value="Tentative">Tentative</option>
                            <option value="Waitlist">Waitlist</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Day use</label>
                          <select
                            value={formData.day_use}
                            onChange={(e) => setFormData(prev => ({ ...prev, day_use: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          >
                            <option value="No">No</option>
                            <option value="Yes">Yes</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Board Type</label>
                          <select
                            value={formData.board_type}
                            onChange={(e) => setFormData(prev => ({ ...prev, board_type: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          >
                            {(boardTypes.length
                              ? boardTypes.map((row) => row.name)
                              : ['Room Only', 'Breakfast', 'Half Board', 'Full Board']
                            ).map((name) => (
                              <option key={name} value={name}>{name}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Rooms</label>
                          <div className="flex gap-2">
                            <select
                              value={formData.rooms_count}
                              onChange={(e) => {
                                const count = parseInt(e.target.value)
                                const currentCount = formData.rooms.length
                                if (count > currentCount) {
                                  addRoom()
                                } else if (count < currentCount) {
                                  removeRoom(currentCount - 1)
                                }
                              }}
                              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            >
                              {[1, 2, 3, 4, 5].map(n => (
                                <option key={n} value={n}>{n}</option>
                              ))}
                            </select>
                            <button
                              type="button"
                              onClick={addRoom}
                              className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                            >
                              <Plus className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Rooms */}
                      {formData.rooms.map((room, index) => (
                        <div key={index} className="mb-6 p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-gray-900">ROOM - {index + 1}</h3>
                            {formData.rooms.length > 1 && (
                              <button
                                type="button"
                                onClick={() => removeRoom(index)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-5 w-5" />
                              </button>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Room Type</label>
                              <select
                                value={room.room_type_id || ''}
                                onChange={(e) => updateRoom(index, 'room_type_id', e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                <option value="">Select Room Type</option>
                                {roomTypes.map(type => (
                                  <option key={type.id} value={type.id}>
                                    {type.name} {type.base_rate && `(${formatMoney(type.base_rate)}/night)`}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Room <span className="text-red-500">*</span>
                              </label>
                              <select
                                value={room.room_id || ''}
                                onChange={(e) => updateRoom(index, 'room_id', e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                disabled={calculating}
                              >
                                <option value="">Select Room</option>
                                {availableRooms
                                  .filter(r => !room.room_type_id || r.room_type.id === room.room_type_id)
                                  .map(r => (
                                    <option key={r.id} value={r.id}>
                                      {r.room_number} - {r.room_type.name}
                                    </option>
                                  ))}
                              </select>
                              {errors[`room_${index}`] && (
                                <p className="mt-1 text-sm text-red-600">{errors[`room_${index}`]}</p>
                              )}
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Adult(s)</label>
                              <select
                                value={room.adults}
                                onChange={(e) => updateRoom(index, 'adults', parseInt(e.target.value))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                {[1, 2, 3, 4, 5, 6].map(n => (
                                  <option key={n} value={n}>{n}</option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Child(s)</label>
                              <select
                                value={room.children}
                                onChange={(e) => updateRoom(index, 'children', parseInt(e.target.value))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                {[0, 1, 2, 3, 4].map(n => (
                                  <option key={n} value={n}>{n}</option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Ex.Bed</label>
                              <select
                                value={room.extra_bed}
                                onChange={(e) => updateRoom(index, 'extra_bed', e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                <option value="No">No</option>
                                <option value="Yes">Yes</option>
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Ex.B.Charge</label>
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={room.extra_bed_charge}
                                onChange={(e) => updateRoom(index, 'extra_bed_charge', parseFloat(e.target.value) || 0)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                disabled={room.extra_bed === 'No'}
                              />
                            </div>
                          </div>

                          {/* Pricing Breakdown */}
                          <div className="border-t pt-4">
                            <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                              <div className="font-medium text-gray-700">Room Rent</div>
                              <div className="text-right">
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={room.room_rate}
                                  onChange={(e) => updateRoom(index, 'room_rate', parseFloat(e.target.value) || 0)}
                                  className="w-full px-2 py-1 border border-gray-300 rounded text-right"
                                />
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                              <div className="font-medium text-gray-700">SC</div>
                              <div className="text-right">
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={room.service_charge}
                                  onChange={(e) => updateRoom(index, 'service_charge', parseFloat(e.target.value) || 0)}
                                  className="w-full px-2 py-1 border border-gray-300 rounded text-right"
                                />
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                              <div className="font-medium text-gray-700">Vat</div>
                              <div className="text-right">
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={room.vat}
                                  onChange={(e) => updateRoom(index, 'vat', parseFloat(e.target.value) || 0)}
                                  className="w-full px-2 py-1 border border-gray-300 rounded text-right"
                                />
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm mb-2 border-t pt-2">
                              <div className="font-medium text-gray-900">Sub Total</div>
                              <div className="text-right font-semibold">{formatMoney(room.sub_total)}</div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm border-t pt-2">
                              <div className="font-bold text-gray-900">Total Rent</div>
                              <div className="text-right font-bold text-indigo-600">{formatMoney(room.total_rent)}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Right Column - Guest Information */}
                  <div className="space-y-6">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h2 className="text-xl font-semibold text-gray-900 mb-4">GUEST INFORMATION</h2>

                      <div className="mb-4">
                        <label className="flex items-center gap-2 mb-2">
                          <input
                            type="checkbox"
                            checked={formData.use_existing_guest}
                            onChange={(e) => {
                              setFormData(prev => ({
                                ...prev,
                                use_existing_guest: e.target.checked,
                                guest_id: null,
                                guest_search: ''
                              }))
                            }}
                            className="rounded"
                          />
                          <span className="text-sm font-medium text-gray-700">Use existing guest</span>
                        </label>
                      </div>

                      {formData.use_existing_guest ? (
                        <div className="mb-4">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Search Guest
                          </label>
                          <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                              type="text"
                              value={formData.guest_search}
                              onChange={(e) => {
                                setFormData(prev => ({ ...prev, guest_search: e.target.value }))
                                searchGuests(e.target.value)
                                setShowGuestSearch(true)
                              }}
                              placeholder="Search by name, email, or phone..."
                              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            />
                            {showGuestSearch && searchResults.length > 0 && (
                              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                {searchResults.map((guest) => (
                                  <div
                                    key={guest.id}
                                    onClick={() => selectGuest(guest)}
                                    className="p-3 hover:bg-gray-200 cursor-pointer border-b border-gray-100 last:border-b-0"
                                  >
                                    <div className="flex items-center justify-between">
                                      <div>
                                        <p className="font-medium text-gray-900">{guest.name}</p>
                                        {guest.email && <p className="text-sm text-gray-600">{guest.email}</p>}
                                        {guest.phone && <p className="text-sm text-gray-600">{guest.phone}</p>}
                                      </div>
                                      {guest.is_vip && (
                                        <span className="text-xs bg-yellow-400 text-yellow-900 px-2 py-1 rounded">VIP</span>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Mobile number</label>
                              <div className="flex gap-2">
                                <select
                                  value={formData.guest.country_code}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, country_code: e.target.value }
                                  }))}
                                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                >
                                  <option value="+880">BD +880</option>
                                  <option value="+1">US +1</option>
                                  <option value="+91">IN +91</option>
                                </select>
                                <input
                                  type="tel"
                                  value={formData.guest.mobile}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, mobile: e.target.value }
                                  }))}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                  placeholder="Mobile number"
                                />
                              </div>
                              {errors['guest.mobile'] && (
                                <p className="mt-1 text-sm text-red-600">{errors['guest.mobile']}</p>
                              )}
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Guest Name</label>
                              <div className="flex gap-2">
                                <select
                                  value={formData.guest.title}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, title: e.target.value }
                                  }))}
                                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                >
                                  <option value="Mr">Mr.</option>
                                  <option value="Mrs">Mrs.</option>
                                  <option value="Miss">Miss.</option>
                                  <option value="Dr">Dr.</option>
                                </select>
                                <input
                                  type="text"
                                  value={formData.guest.first_name}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, first_name: e.target.value }
                                  }))}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                  placeholder="First Name"
                                />
                                <input
                                  type="text"
                                  value={formData.guest.last_name}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, last_name: e.target.value }
                                  }))}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                  placeholder="Last Name"
                                />
                              </div>
                              {errors['guest.first_name'] && (
                                <p className="mt-1 text-sm text-red-600">{errors['guest.first_name']}</p>
                              )}
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                              <div className="flex gap-2">
                                <select
                                  value={formData.guest.gender}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, gender: e.target.value }
                                  }))}
                                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                >
                                  <option value="Male">Male</option>
                                  <option value="Female">Female</option>
                                  <option value="Other">Other</option>
                                </select>
                                <input
                                  type="text"
                                  value={formData.guest.company}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, company: e.target.value }
                                  }))}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                  placeholder="Company"
                                />
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                              <input
                                type="email"
                                value={formData.guest.email}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, email: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Email"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
                              <input
                                type="date"
                                value={formData.guest.date_of_birth}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, date_of_birth: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Profession</label>
                              <input
                                type="text"
                                value={formData.guest.profession}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, profession: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Profession"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Father/Husband</label>
                              <input
                                type="text"
                                value={formData.guest.father_husband}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, father_husband: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Father/Husband Name"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                              <div className="flex gap-2">
                                <select
                                  value={formData.guest.country}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, country: e.target.value }
                                  }))}
                                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                >
                                  <option value="Bangladesh">Bangladesh</option>
                                  <option value="India">India</option>
                                  <option value="USA">USA</option>
                                </select>
                                <input
                                  type="text"
                                  value={formData.guest.address_line1}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, address_line1: e.target.value }
                                  }))}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                  placeholder="Address"
                                />
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Identity Type</label>
                              <select
                                value={formData.guest.id_type}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, id_type: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                <option value="">Select Identity Type</option>
                                <option value="Passport">Passport</option>
                                <option value="NID">National ID</option>
                                <option value="Driving License">Driving License</option>
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Identity No</label>
                              <input
                                type="text"
                                value={formData.guest.id_number}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, id_number: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Identity Number"
                              />
                            </div>

                            <div className="col-span-2">
                              <label className="block text-sm font-medium text-gray-700 mb-2">Identity Image</label>
                              <div className="flex items-center gap-2">
                                <input
                                  type="file"
                                  accept="image/*"
                                  onChange={(e) => {
                                    const file = e.target.files?.[0]
                                    if (file) {
                                      setFormData(prev => ({
                                        ...prev,
                                        guest: { ...prev.guest, id_image: file }
                                      }))
                                    }
                                  }}
                                  className="hidden"
                                  id="id-image-upload"
                                />
                                <label
                                  htmlFor="id-image-upload"
                                  className="px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 flex items-center gap-2"
                                >
                                  <Upload className="h-4 w-4" />
                                  Choose File
                                </label>
                                <span className="text-sm text-gray-500">
                                  {formData.guest.id_image ? formData.guest.id_image.name : 'No file chosen'}
                                </span>
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
                              <select
                                value={formData.guest.source}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, source: e.target.value }
                                }))}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                              >
                                <option value="">Select Source</option>
                                {(guestSources.length
                                  ? guestSources.map((row) => row.name)
                                  : ['Online', 'Phone', 'Walk-in', 'Agent']
                                ).map((name) => (
                                  <option key={name} value={name}>{name}</option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="flex items-center gap-2 mt-6">
                                <input
                                  type="checkbox"
                                  checked={formData.guest.is_vip}
                                  onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    guest: { ...prev.guest, is_vip: e.target.checked }
                                  }))}
                                  className="rounded"
                                />
                                <span className="text-sm font-medium text-gray-700">VIP Guest</span>
                              </label>
                            </div>

                            <div className="col-span-2">
                              <label className="block text-sm font-medium text-gray-700 mb-2">Comments</label>
                              <textarea
                                value={formData.guest.comments}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  guest: { ...prev.guest, comments: e.target.value }
                                }))}
                                rows={3}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Additional comments..."
                              />
                            </div>
                          </div>
                        </>
                      )}
                    </div>

                    {/* Payment Summary */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Summary</h2>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Total Amount</span>
                          <span className="font-semibold text-indigo-600">{formatMoney(formData.total_amount)}</span>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Paid Amount</label>
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.paid_amount}
                            onChange={(e) => setFormData(prev => ({
                              ...prev,
                              paid_amount: parseFloat(e.target.value) || 0
                            }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                          />
                        </div>
                        <div className="border-t pt-3">
                          <div className="flex justify-between">
                            <span className="font-medium text-gray-900">Balance</span>
                            <span className={`font-semibold ${(formData.total_amount - formData.paid_amount) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {formatMoney(formData.total_amount - formData.paid_amount)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'sharer' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900">Sharer Information</h2>
                    <button
                      type="button"
                      onClick={() => setFormData((prev) => ({
                        ...prev,
                        sharers: [...prev.sharers, { name: '', relation: '', id_number: '' }]
                      }))}
                      className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white"
                    >
                      Add Sharer
                    </button>
                  </div>
                  <div className="space-y-3">
                    {formData.sharers.map((sharer, index) => (
                      <div key={index} className="grid gap-3 rounded-lg border p-3 md:grid-cols-3">
                        <input
                          placeholder="Full name"
                          value={sharer.name}
                          onChange={(e) => setFormData((prev) => {
                            const sharers = [...prev.sharers]
                            sharers[index] = { ...sharers[index], name: e.target.value }
                            return { ...prev, sharers }
                          })}
                          className="rounded-lg border px-3 py-2"
                        />
                        <input
                          placeholder="Relation"
                          value={sharer.relation}
                          onChange={(e) => setFormData((prev) => {
                            const sharers = [...prev.sharers]
                            sharers[index] = { ...sharers[index], relation: e.target.value }
                            return { ...prev, sharers }
                          })}
                          className="rounded-lg border px-3 py-2"
                        />
                        <input
                          placeholder="ID number"
                          value={sharer.id_number}
                          onChange={(e) => setFormData((prev) => {
                            const sharers = [...prev.sharers]
                            sharers[index] = { ...sharers[index], id_number: e.target.value }
                            return { ...prev, sharers }
                          })}
                          className="rounded-lg border px-3 py-2"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'pickup' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Pickup/Drop Information</h2>
                  <div className="grid gap-4 md:grid-cols-2">
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={formData.pickup.pickup_required}
                        onChange={(e) => setFormData((prev) => ({
                          ...prev,
                          pickup: { ...prev.pickup, pickup_required: e.target.checked }
                        }))}
                      />
                      Pickup required
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={formData.pickup.drop_required}
                        onChange={(e) => setFormData((prev) => ({
                          ...prev,
                          pickup: { ...prev.pickup, drop_required: e.target.checked }
                        }))}
                      />
                      Drop required
                    </label>
                    <input
                      placeholder="Pickup from"
                      value={formData.pickup.pickup_from}
                      onChange={(e) => setFormData((prev) => ({
                        ...prev,
                        pickup: { ...prev.pickup, pickup_from: e.target.value }
                      }))}
                      className="rounded-lg border px-3 py-2"
                    />
                    <input
                      type="time"
                      value={formData.pickup.pickup_time}
                      onChange={(e) => setFormData((prev) => ({
                        ...prev,
                        pickup: { ...prev.pickup, pickup_time: e.target.value }
                      }))}
                      className="rounded-lg border px-3 py-2"
                    />
                    <input
                      placeholder="Drop to"
                      value={formData.pickup.drop_to}
                      onChange={(e) => setFormData((prev) => ({
                        ...prev,
                        pickup: { ...prev.pickup, drop_to: e.target.value }
                      }))}
                      className="rounded-lg border px-3 py-2"
                    />
                    <input
                      type="time"
                      value={formData.pickup.drop_time}
                      onChange={(e) => setFormData((prev) => ({
                        ...prev,
                        pickup: { ...prev.pickup, drop_time: e.target.value }
                      }))}
                      className="rounded-lg border px-3 py-2"
                    />
                    <input
                      placeholder="Vehicle / flight / train"
                      value={formData.pickup.vehicle}
                      onChange={(e) => setFormData((prev) => ({
                        ...prev,
                        pickup: { ...prev.pickup, vehicle: e.target.value }
                      }))}
                      className="rounded-lg border px-3 py-2 md:col-span-2"
                    />
                  </div>
                </div>
              )}

              {activeTab === 'complimentaries' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900">Complimentaries</h2>
                    <button
                      type="button"
                      onClick={() => setFormData((prev) => ({
                        ...prev,
                        complimentaries: [...prev.complimentaries, { item: '', quantity: 1, notes: '' }]
                      }))}
                      className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white"
                    >
                      Add Item
                    </button>
                  </div>
                  <div className="space-y-3">
                    {formData.complimentaries.map((row, index) => (
                      <div key={index} className="grid gap-3 rounded-lg border p-3 md:grid-cols-3">
                        {compOptions.length ? (
                          <select
                            value={row.item}
                            onChange={(e) => setFormData((prev) => {
                              const complimentaries = [...prev.complimentaries]
                              complimentaries[index] = { ...complimentaries[index], item: e.target.value }
                              return { ...prev, complimentaries }
                            })}
                            className="rounded-lg border px-3 py-2"
                          >
                            <option value="">Select item…</option>
                            {compOptions.map((opt) => (
                              <option key={opt.id} value={opt.name}>{opt.name}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            placeholder="Item (breakfast, fruit basket…)"
                            value={row.item}
                            onChange={(e) => setFormData((prev) => {
                              const complimentaries = [...prev.complimentaries]
                              complimentaries[index] = { ...complimentaries[index], item: e.target.value }
                              return { ...prev, complimentaries }
                            })}
                            className="rounded-lg border px-3 py-2"
                          />
                        )}
                        <input
                          type="number"
                          min={1}
                          value={row.quantity}
                          onChange={(e) => setFormData((prev) => {
                            const complimentaries = [...prev.complimentaries]
                            complimentaries[index] = { ...complimentaries[index], quantity: parseInt(e.target.value) || 1 }
                            return { ...prev, complimentaries }
                          })}
                          className="rounded-lg border px-3 py-2"
                        />
                        <input
                          placeholder="Notes"
                          value={row.notes}
                          onChange={(e) => setFormData((prev) => {
                            const complimentaries = [...prev.complimentaries]
                            complimentaries[index] = { ...complimentaries[index], notes: e.target.value }
                            return { ...prev, complimentaries }
                          })}
                          className="rounded-lg border px-3 py-2"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Form Actions */}
              <div className="flex items-center justify-end gap-4 pt-6 border-t">
                {errors.submit && (
                  <div className="flex-1 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <p className="text-sm text-red-800">{errors.submit}</p>
                  </div>
                )}
                <button
                  type="button"
                  onClick={() => router.back()}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
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
                      Create Reservation
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

