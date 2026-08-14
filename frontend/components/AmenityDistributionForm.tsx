'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function AmenityDistributionForm() {
  const [rooms, setRooms] = useState<{ id: number; name: string }[]>([])
  const [roomId, setRoomId] = useState('')
  const [itemName, setItemName] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [saved, setSaved] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiClient.get('/housekeeping/amenity-distribution').then((res) => {
      const opts = res.data.options?.rooms || []
      setRooms(opts)
      if (opts[0]) setRoomId(String(opts[0].id))
    })
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSaved('')
    try {
      await apiClient.post('/housekeeping/amenity-distribution', {
        room_id: Number(roomId),
        item_name: itemName,
        quantity: Number(quantity),
        notes,
      })
      setItemName('')
      setQuantity('1')
      setSaved('Distribution posted.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Amenity Distribution — Create</h1>
          <p className="mt-1 text-gray-600">Issue amenities to a room (soap, water, slippers, etc.).</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {saved && <p className="mt-4 text-emerald-700">{saved}</p>}
          <form onSubmit={submit} className="mt-6 grid max-w-xl gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2">
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Room *</span>
              <select className="w-full rounded-lg border px-3 py-2" required value={roomId} onChange={(e) => setRoomId(e.target.value)}>
                <option value="">Select…</option>
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Amenity *</span>
              <input className="w-full rounded-lg border px-3 py-2" required value={itemName} onChange={(e) => setItemName(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Quantity *</span>
              <input type="number" min="1" className="w-full rounded-lg border px-3 py-2" required value={quantity} onChange={(e) => setQuantity(e.target.value)} />
            </label>
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Notes</span>
              <textarea className="w-full rounded-lg border px-3 py-2" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
            </label>
            <div>
              <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
                {saving ? 'Saving…' : 'Post distribution'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
