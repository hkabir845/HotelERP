'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { BANQUET_EVENT_TYPES } from '@/lib/banquet-config'
import { formatMoney } from '@/lib/money'
import { Plus, Trash2 } from 'lucide-react'

type Opt = {
  id: number | string
  name: string
  unit_price?: number
  rate?: number
  price_per_pax?: number
  start_time?: string
  end_time?: string
}

type Line = {
  line_type: 'service' | 'item' | 'vendor'
  ref_id: string
  quantity: string
  unit_price: string
}

function emptyLine(): Line {
  return { line_type: 'service', ref_id: '', quantity: '1', unit_price: '' }
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

function catalogFor(options: Record<string, Opt[]>, type: Line['line_type']) {
  if (type === 'item') return options.items || []
  if (type === 'vendor') return options.vendors || []
  return options.services || []
}

function defaultPrice(row: Opt | undefined, type: Line['line_type']) {
  if (!row) return ''
  if (type === 'vendor') return String(row.rate ?? '')
  return String(row.unit_price ?? '')
}

export default function BanquetEventForm() {
  const router = useRouter()
  const [options, setOptions] = useState<Record<string, Opt[]>>({})
  const [name, setName] = useState('')
  const [eventType, setEventType] = useState('wedding')
  const [contactName, setContactName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [company, setCompany] = useState('')
  const [venueId, setVenueId] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [eventDate, setEventDate] = useState(today())
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [pax, setPax] = useState('')
  const [packageId, setPackageId] = useState('')
  const [notes, setNotes] = useState('')
  const [lines, setLines] = useState<Line[]>([emptyLine()])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiClient
      .get('/banquet/config/venues')
      .then((res) => {
        const opts = res.data.options || {}
        setOptions(opts)
        const venues = opts.venues || []
        const sessions = opts.sessions || []
        if (venues[0] && !venueId) setVenueId(String(venues[0].id))
        if (sessions[0] && !sessionId) {
          setSessionId(String(sessions[0].id))
          setStartTime(sessions[0].start_time || '')
          setEndTime(sessions[0].end_time || '')
        }
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load banquet masters'))
  }, [])

  const pkg = (options.packages || []).find((row) => String(row.id) === packageId)
  const packageAmount = (Number(pax || 0) * Number(pkg?.price_per_pax || 0)) || 0
  const linesAmount = useMemo(
    () =>
      lines.reduce((sum, line) => {
        if (!line.ref_id) return sum
        return sum + Number(line.quantity || 0) * Number(line.unit_price || 0)
      }, 0),
    [lines]
  )
  const total = packageAmount + linesAmount

  const setSession = (id: string) => {
    setSessionId(id)
    const sess = (options.sessions || []).find((row) => String(row.id) === id)
    if (sess) {
      setStartTime(sess.start_time || '')
      setEndTime(sess.end_time || '')
    }
  }

  const updateLine = (index: number, key: keyof Line, value: string) => {
    setLines((prev) =>
      prev.map((line, i) => {
        if (i !== index) return line
        const next = { ...line, [key]: value }
        if (key === 'line_type') {
          next.ref_id = ''
          next.unit_price = ''
          next.line_type = value as Line['line_type']
        }
        if (key === 'ref_id') {
          const row = catalogFor(options, next.line_type).find((item) => String(item.id) === value)
          next.unit_price = defaultPrice(row, next.line_type)
        }
        return next
      })
    )
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/banquet/events', {
        name,
        event_type: eventType,
        contact_name: contactName,
        phone,
        email,
        company,
        venue_id: venueId || null,
        session_id: sessionId || null,
        event_date: eventDate,
        start_time: startTime,
        end_time: endTime,
        pax: Number(pax || 0),
        package_id: packageId || null,
        notes,
        lines: lines
          .filter((line) => line.ref_id && Number(line.quantity) > 0)
          .map((line) => ({
            line_type: line.line_type,
            ref_id: Number(line.ref_id),
            quantity: Number(line.quantity),
            unit_price: Number(line.unit_price || 0),
          })),
      })
      router.push('/banquet/events')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const money = (n: number) => formatMoney(n)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Create Event</h1>
          <p className="mt-1 text-gray-600">
            Book a venue and session, attach a set menu, then add services, items, and vendors to the folio.
          </p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <form onSubmit={submit} className="mt-6 space-y-4">
            <div className="grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4">
              <label className="text-sm sm:col-span-2">
                <span className="mb-1 block text-slate-600">Event name *</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Type</span>
                <select
                  className="w-full rounded-lg border px-3 py-2"
                  value={eventType}
                  onChange={(e) => setEventType(e.target.value)}
                >
                  {BANQUET_EVENT_TYPES.map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Event date *</span>
                <input
                  type="date"
                  className="w-full rounded-lg border px-3 py-2"
                  required
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Venue</span>
                <select
                  className="w-full rounded-lg border px-3 py-2"
                  value={venueId}
                  onChange={(e) => setVenueId(e.target.value)}
                >
                  <option value="">Select…</option>
                  {(options.venues || []).map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Session</span>
                <select
                  className="w-full rounded-lg border px-3 py-2"
                  value={sessionId}
                  onChange={(e) => setSession(e.target.value)}
                >
                  <option value="">Select…</option>
                  {(options.sessions || []).map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.name}
                      {row.start_time ? ` (${row.start_time}–${row.end_time})` : ''}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Start</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  placeholder="12:00"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">End</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  placeholder="16:00"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Contact</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Phone</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Email</span>
                <input
                  type="email"
                  className="w-full rounded-lg border px-3 py-2"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Company</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Pax</span>
                <input
                  type="number"
                  min="0"
                  className="w-full rounded-lg border px-3 py-2"
                  value={pax}
                  onChange={(e) => setPax(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Set menu</span>
                <select
                  className="w-full rounded-lg border px-3 py-2"
                  value={packageId}
                  onChange={(e) => setPackageId(e.target.value)}
                >
                  <option value="">None</option>
                  {(options.packages || []).map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.name} ({money(Number(row.price_per_pax || 0))} / pax)
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm sm:col-span-2 lg:col-span-4">
                <span className="mb-1 block text-slate-600">Notes</span>
                <textarea
                  className="w-full rounded-lg border px-3 py-2"
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </label>
            </div>

            <div className="rounded-xl border bg-white p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-semibold">Services, items & vendors</h2>
                <button
                  type="button"
                  onClick={() => setLines((prev) => [...prev, emptyLine()])}
                  className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm"
                >
                  <Plus className="h-4 w-4" />
                  Add line
                </button>
              </div>
              <table className="min-w-full text-sm">
                <thead className="text-left text-slate-600">
                  <tr>
                    <th className="pb-2 font-medium">Type</th>
                    <th className="pb-2 font-medium">Catalog</th>
                    <th className="pb-2 font-medium">Qty</th>
                    <th className="pb-2 font-medium">Rate</th>
                    <th className="pb-2 font-medium">Amount</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {lines.map((line, index) => {
                    const catalog = catalogFor(options, line.line_type)
                    const amount = Number(line.quantity || 0) * Number(line.unit_price || 0)
                    return (
                      <tr key={index} className="border-t">
                        <td className="py-2 pr-2">
                          <select
                            className="w-full rounded border px-2 py-1"
                            value={line.line_type}
                            onChange={(e) => updateLine(index, 'line_type', e.target.value)}
                          >
                            <option value="service">Service</option>
                            <option value="item">Item</option>
                            <option value="vendor">Vendor</option>
                          </select>
                        </td>
                        <td className="py-2 pr-2">
                          <select
                            className="w-full rounded border px-2 py-1"
                            value={line.ref_id}
                            onChange={(e) => updateLine(index, 'ref_id', e.target.value)}
                          >
                            <option value="">Select…</option>
                            {catalog.map((row) => (
                              <option key={row.id} value={row.id}>
                                {row.name}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="py-2 pr-2 w-24">
                          <input
                            type="number"
                            min="0"
                            className="w-full rounded border px-2 py-1"
                            value={line.quantity}
                            onChange={(e) => updateLine(index, 'quantity', e.target.value)}
                          />
                        </td>
                        <td className="py-2 pr-2 w-28">
                          <input
                            type="number"
                            min="0"
                            className="w-full rounded border px-2 py-1"
                            value={line.unit_price}
                            onChange={(e) => updateLine(index, 'unit_price', e.target.value)}
                          />
                        </td>
                        <td className="py-2 pr-2 text-right">{money(amount)}</td>
                        <td className="py-2">
                          <button
                            type="button"
                            onClick={() => setLines((prev) => prev.filter((_, i) => i !== index))}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-white p-4">
              <div className="flex flex-wrap gap-6 text-sm">
                <div>
                  <div className="text-slate-500">Set menu</div>
                  <div className="font-semibold">{money(packageAmount)}</div>
                </div>
                <div>
                  <div className="text-slate-500">Lines</div>
                  <div className="font-semibold">{money(linesAmount)}</div>
                </div>
                <div>
                  <div className="text-slate-500">Quoted total</div>
                  <div className="font-semibold">{money(total)}</div>
                </div>
              </div>
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save event'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
