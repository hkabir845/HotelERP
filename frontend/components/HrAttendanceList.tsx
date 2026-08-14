'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

function monthStart() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function HrAttendanceList() {
  const [from, setFrom] = useState(monthStart())
  const [to, setTo] = useState(today())
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    apiClient
      .get(`/hr/attendance?from=${from}&to=${to}`)
      .then((res) => setItems(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Attendance List</h1>
          <p className="mt-1 text-gray-600">Daily punch records with hours and late fines.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">From</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={from} onChange={(e) => setFrom(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">To</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={to} onChange={(e) => setTo(e.target.value)} />
            </label>
            <button type="button" onClick={load} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
              Run
            </button>
          </div>
          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {['Date', 'Employee', 'Dept', 'In', 'Out', 'Hours', 'Late min', 'Fine', 'Status'].map((h) => (
                    <th key={h} className="px-3 py-2 font-medium">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-10 text-center text-slate-500">
                      Loading…
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-10 text-center text-slate-500">
                      No attendance in this period.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-3 py-2">{row.attendance_date}</td>
                      <td className="px-3 py-2">{row.employee_name}</td>
                      <td className="px-3 py-2">{row.department || '—'}</td>
                      <td className="px-3 py-2">{row.check_in || '—'}</td>
                      <td className="px-3 py-2">{row.check_out || '—'}</td>
                      <td className="px-3 py-2">{row.hours_worked}</td>
                      <td className="px-3 py-2">{row.late_minutes}</td>
                      <td className="px-3 py-2">{row.late_fine}</td>
                      <td className="px-3 py-2">{row.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
