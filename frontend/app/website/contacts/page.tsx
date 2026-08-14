'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

type Contact = {
  id: number
  name: string
  email: string
  phone: string
  subject: string
  message: string
  status: string
  created_at?: string | null
}

export default function WebsiteContactsPage() {
  const [rows, setRows] = useState<Contact[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get('/website/contacts')
      .then((res) => setRows(res.data.contacts || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load contacts'))
  }, [])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Contact inbox</h1>
          <p className="mt-1 text-gray-600">Messages from the public website contact form.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-6 overflow-hidden rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3">When</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3">Message</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                      No messages yet.
                    </td>
                  </tr>
                )}
                {rows.map((r) => (
                  <tr key={r.id} className="border-t">
                    <td className="px-4 py-3 text-slate-500">{r.created_at?.slice(0, 16)?.replace('T', ' ')}</td>
                    <td className="px-4 py-3 font-medium">{r.name}</td>
                    <td className="px-4 py-3">{r.email}</td>
                    <td className="px-4 py-3">{r.phone}</td>
                    <td className="px-4 py-3 max-w-md truncate">{r.message}</td>
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
