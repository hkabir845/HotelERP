'use client'

import { useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function ClearCachePage() {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const res = await apiClient.post('/utilities/clear-cache')
      setMessage(res.data.detail || 'Cache cleared.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Clear failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Clear Cache</h1>
          <p className="mt-1 text-gray-600">Flush the application cache. This does not delete reservations, folios, or masters.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {message && <p className="mt-4 text-emerald-700">{message}</p>}
          <button
            type="button"
            onClick={run}
            disabled={busy}
            className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {busy ? 'Clearing…' : 'Clear cache now'}
          </button>
        </main>
      </div>
    </ProtectedRoute>
  )
}
