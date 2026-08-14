'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'

export default function AdditionalConfigPage() {
  const [form, setForm] = useState({
    check_in_time: '14:00',
    check_out_time: '12:00',
    tax_percent: '0',
    service_charge_percent: '0',
    sms_unit_cost: '0.5',
    night_audit_time: '23:59',
  })
  const [error, setError] = useState('')
  const [saved, setSaved] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiClient
      .get('/utilities/additional-configs')
      .then((res) =>
        setForm({
          check_in_time: res.data.check_in_time || '14:00',
          check_out_time: res.data.check_out_time || '12:00',
          tax_percent: String(res.data.tax_percent ?? 0),
          service_charge_percent: String(res.data.service_charge_percent ?? 0),
          sms_unit_cost: String(res.data.sms_unit_cost ?? 0.5),
          night_audit_time: res.data.night_audit_time || '23:59',
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
      await apiClient.put('/utilities/additional-configs', form)
      setSaved('Saved.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const fields: [keyof typeof form, string][] = [
    ['check_in_time', 'Check-in time'],
    ['check_out_time', 'Check-out time'],
    ['night_audit_time', 'Night audit time'],
    ['tax_percent', 'Tax %'],
    ['service_charge_percent', 'Service charge %'],
    ['sms_unit_cost', 'SMS unit cost'],
  ]

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Additional Configs</h1>
          <p className="mt-1 text-gray-600">Property operating times, tax, and SMS unit cost used on the SMS cost report.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          {saved && <p className="mt-4 text-emerald-700">{saved}</p>}
          <form onSubmit={submit} className="mt-6 grid max-w-xl gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2">
            {fields.map(([key, label]) => (
              <label key={key} className="text-sm">
                <span className="mb-1 block text-slate-600">{label}</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={form[key]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
                />
              </label>
            ))}
            <div className="sm:col-span-2">
              <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
                {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
