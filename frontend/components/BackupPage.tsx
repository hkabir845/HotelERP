'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

type Snapshot = {
  id: number
  name: string
  code: string
  notes: string
  created_at: string
}

export default function BackupPage() {
  const [items, setItems] = useState<Snapshot[]>([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => {
    apiClient
      .get('/utilities/backup')
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load snapshots'))
  }

  useEffect(() => {
    load()
  }, [])

  const run = async () => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const res = await apiClient.post('/utilities/backup', {})
      setMessage(res.data.detail || 'Snapshot recorded.')
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Backup failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Backup & Restore</h1>
          <p className="mt-1 text-gray-600">
            Record a live data snapshot (reservation, room, guest, and voucher counts) and flush the
            application cache. This does not dump the database file.
          </p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {message && <p className="mt-4 text-emerald-700">{message}</p>}
          <button
            type="button"
            onClick={run}
            disabled={busy}
            className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {busy ? 'Recording…' : 'Take snapshot now'}
          </button>
          <div className="mt-6 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-3 py-2">Snapshot</th>
                  <th className="px-3 py-2">Code</th>
                  <th className="px-3 py-2">Counts</th>
                </tr>
              </thead>
              <tbody>
                {items.map((row) => (
                  <tr key={row.id} className="border-t">
                    <td className="px-3 py-2">{row.name}</td>
                    <td className="px-3 py-2">{row.code}</td>
                    <td className="px-3 py-2">{row.notes}</td>
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
