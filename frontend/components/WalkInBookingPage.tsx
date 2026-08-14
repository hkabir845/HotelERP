'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

function today() {
  return new Date().toISOString().slice(0, 10)
}

function tomorrow() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

export default function WalkInBookingPage() {
  const router = useRouter()
  const [rooms, setRooms] = useState<any[]>([])
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [idNumber, setIdNumber] = useState('')
  const [checkIn, setCheckIn] = useState(today())
  const [checkOut, setCheckOut] = useState(tomorrow())
  const [roomId, setRoomId] = useState('')
  const [adults, setAdults] = useState('1')
  const [paid, setPaid] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiClient
      .get(`/reservations/rooms/available?check_in=${checkIn}&check_out=${checkOut}`)
      .then((res) => {
        const list = res.data.rooms || res.data.items || []
        setRooms(list)
        if (list[0] && !roomId) setRoomId(String(list[0].id))
      })
      .catch(() => {
        apiClient.get('/frontdesk/config/rooms').then((res) => {
          const list = (res.data.items || []).filter((r: any) => r.status === 'available' || r.is_active)
          setRooms(list)
        })
      })
  }, [checkIn, checkOut])

  const room = rooms.find((r) => String(r.id) === roomId)
  const rate = Number(room?.rack_rate || room?.base_rate || room?.room_type?.base_rate || 0)
  const nights = useMemo(() => {
    const a = new Date(`${checkIn}T14:00:00`)
    const b = new Date(`${checkOut}T14:00:00`)
    return Math.max(1, Math.round((b.getTime() - a.getTime()) / 86400000))
  }, [checkIn, checkOut])
  const total = rate * nights

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/reservations/create', {
        guest: { first_name: firstName, last_name: lastName, phone, id_number: idNumber },
        room_id: roomId ? Number(roomId) : null,
        check_in_date: `${checkIn}T14:00:00`,
        check_out_date: `${checkOut}T14:00:00`,
        room_rate: rate,
        total_amount: total,
        paid_amount: Number(paid || 0),
        adults: Number(adults || 1),
        status: 'confirmed',
        reservation_type: 'walk_in',
        notes,
      })
      router.push('/frontdesk/reservations')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Booking failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Add Booking</h1>
          <p className="mt-1 text-gray-600">
            Walk-in / confirmed booking. Assign a room now; this is separate from a future reservation hold.
          </p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <form onSubmit={submit} className="mt-6 grid max-w-4xl gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">First name *</span>
              <input className="w-full rounded-lg border px-3 py-2" required value={firstName} onChange={(e) => setFirstName(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Last name *</span>
              <input className="w-full rounded-lg border px-3 py-2" required value={lastName} onChange={(e) => setLastName(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Phone</span>
              <input className="w-full rounded-lg border px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">ID number</span>
              <input className="w-full rounded-lg border px-3 py-2" value={idNumber} onChange={(e) => setIdNumber(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Check in *</span>
              <input type="date" className="w-full rounded-lg border px-3 py-2" required value={checkIn} onChange={(e) => setCheckIn(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Check out *</span>
              <input type="date" className="w-full rounded-lg border px-3 py-2" required value={checkOut} onChange={(e) => setCheckOut(e.target.value)} />
            </label>
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Room</span>
              <select className="w-full rounded-lg border px-3 py-2" value={roomId} onChange={(e) => setRoomId(e.target.value)}>
                <option value="">Select…</option>
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.room_number || r.name} {r.room_type?.name || r.room_type_name || ''}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Adults</span>
              <input type="number" min="1" className="w-full rounded-lg border px-3 py-2" value={adults} onChange={(e) => setAdults(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Advance paid</span>
              <input type="number" min="0" className="w-full rounded-lg border px-3 py-2" value={paid} onChange={(e) => setPaid(e.target.value)} />
            </label>
            <label className="text-sm sm:col-span-2 lg:col-span-3">
              <span className="mb-1 block text-slate-600">Notes</span>
              <textarea className="w-full rounded-lg border px-3 py-2" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
            </label>
            <div className="sm:col-span-2 lg:col-span-3 flex items-center justify-between">
              <div className="text-sm">
                <span className="text-slate-500">{nights} night(s) × {formatMoney(rate)} = </span>
                <span className="font-semibold">{formatMoney(total)}</span>
              </div>
              <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
                {saving ? 'Saving…' : 'Confirm booking'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
