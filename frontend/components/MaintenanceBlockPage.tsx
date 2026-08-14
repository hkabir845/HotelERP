'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function MaintenanceBlockPage() {
  const [items, setItems] = useState<any[]>([])
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')

  const load = () => {
    apiClient
      .get('/housekeeping/maintenance-block')
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [])

  const act = async (id: number, action: string) => {
    setError('')
    try {
      await apiClient.post('/housekeeping/maintenance-block', { room_id: id, action, notes })
      setNotes('')
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Maintenance and Block</h1>
          <p className="mt-1 text-gray-600">Put rooms on maintenance or out of order, then release them back to available.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-4">
            <input
              className="w-full max-w-md rounded-lg border px-3 py-2 text-sm"
              placeholder="Reason / note (saved on next action)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {['Room', 'Type', 'Floor', 'Status', 'Notes', 'Actions'].map((h) => (
                    <th key={h} className="px-3 py-2 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.map((row) => (
                  <tr key={row.id} className="border-t">
                    <td className="px-3 py-2">{row.room_number}</td>
                    <td className="px-3 py-2">{row.room_type}</td>
                    <td className="px-3 py-2">{row.floor ?? '—'}</td>
                    <td className="px-3 py-2 capitalize">{String(row.status).replace(/_/g, ' ')}</td>
                    <td className="px-3 py-2 max-w-xs truncate">{row.notes || '—'}</td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        {!row.blocked && (
                          <>
                            <button type="button" onClick={() => act(row.id, 'block')} className="rounded border px-2 py-1 text-amber-800">Maintenance</button>
                            <button type="button" onClick={() => act(row.id, 'ooo')} className="rounded border px-2 py-1 text-red-700">OOO</button>
                          </>
                        )}
                        {row.blocked && (
                          <button type="button" onClick={() => act(row.id, 'unblock')} className="rounded border px-2 py-1 text-emerald-700">Release</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
