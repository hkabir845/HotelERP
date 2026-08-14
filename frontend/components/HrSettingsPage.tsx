'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function HrSettingsPage() {
  const [form, setForm] = useState({
    work_start: '09:00',
    work_end: '18:00',
    late_grace_minutes: '15',
    late_fine_amount: '50',
    overtime_rate: '0',
  })
  const [error, setError] = useState('')
  const [saved, setSaved] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiClient
      .get('/hr/settings')
      .then((res) =>
        setForm({
          work_start: res.data.work_start || '09:00',
          work_end: res.data.work_end || '18:00',
          late_grace_minutes: String(res.data.late_grace_minutes ?? 15),
          late_fine_amount: String(res.data.late_fine_amount ?? 50),
          overtime_rate: String(res.data.overtime_rate ?? 0),
        })
      )
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSaved('')
    try {
      await apiClient.put('/hr/settings', form)
      setSaved('Settings saved.')
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
          <h1 className="text-3xl font-bold text-gray-900">HR Settings</h1>
          <p className="mt-1 text-gray-600">Default work hours, late grace, and late-fine amount for punch-in.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {saved && <p className="mt-4 text-emerald-700">{saved}</p>}
          <form onSubmit={submit} className="mt-6 grid max-w-xl gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2">
            {(
              [
                ['work_start', 'Work start (HH:MM)'],
                ['work_end', 'Work end (HH:MM)'],
                ['late_grace_minutes', 'Late grace (minutes)'],
                ['late_fine_amount', 'Late fine amount'],
                ['overtime_rate', 'Overtime rate'],
              ] as const
            ).map(([key, label]) => (
              <label key={key} className="text-sm">
                <span className="mb-1 block text-slate-600">{label}</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={(form as any)[key]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
                />
              </label>
            ))}
            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
              >
                {saving ? 'Saving…' : 'Save settings'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
