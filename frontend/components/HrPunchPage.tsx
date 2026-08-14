'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function HrPunchPage() {
  const [employees, setEmployees] = useState<{ id: number; name: string }[]>([])
  const [todayRows, setTodayRows] = useState<any[]>([])
  const [employeeId, setEmployeeId] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => {
    const today = new Date().toISOString().slice(0, 10)
    apiClient.get('/hr/config/employees').then((res) => {
      setEmployees((res.data.options?.employees || []).map((e: any) => ({ id: e.id, name: e.name })))
    })
    apiClient
      .get(`/hr/attendance?from=${today}&to=${today}`)
      .then((res) => setTodayRows(res.data.items || []))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    load()
  }, [])

  const punch = async (action: 'punch_in' | 'punch_out', id?: string) => {
    const emp = id || employeeId
    if (!emp) {
      setError('Select an employee')
      return
    }
    setBusy(true)
    setError('')
    try {
      await apiClient.post('/hr/attendance', { employee_id: Number(emp), action, notes })
      setNotes('')
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Punch failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Punch In/Out</h1>
          <p className="mt-1 text-gray-600">
            Late punch-ins after shift start plus grace minutes post a late fine from HR Settings.
          </p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Employee</span>
              <select
                className="rounded-lg border px-3 py-2"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
              >
                <option value="">Select…</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Note</span>
              <input
                className="rounded-lg border px-3 py-2"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </label>
            <button
              type="button"
              disabled={busy}
              onClick={() => punch('punch_in')}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
            >
              Punch in
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => punch('punch_out')}
              className="rounded-lg border px-4 py-2 text-sm"
            >
              Punch out
            </button>
          </div>
          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  {['Employee', 'In', 'Out', 'Hours', 'Late min', 'Fine', ''].map((h) => (
                    <th key={h} className="px-3 py-2 font-medium">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {todayRows.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-10 text-center text-slate-500">
                      No punches yet today.
                    </td>
                  </tr>
                ) : (
                  todayRows.map((row) => (
                    <tr key={row.id} className="border-t">
                      <td className="px-3 py-2">{row.employee_name}</td>
                      <td className="px-3 py-2">{row.check_in || '—'}</td>
                      <td className="px-3 py-2">{row.check_out || '—'}</td>
                      <td className="px-3 py-2">{row.hours_worked}</td>
                      <td className="px-3 py-2">{row.late_minutes}</td>
                      <td className="px-3 py-2">{row.late_fine}</td>
                      <td className="px-3 py-2">
                        {row.can_punch_out && (
                          <button
                            type="button"
                            onClick={() => punch('punch_out', String(row.employee_id))}
                            className="rounded border px-2 py-1 text-indigo-700"
                          >
                            Punch out
                          </button>
                        )}
                      </td>
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
