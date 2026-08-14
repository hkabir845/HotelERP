'use client'

import { useEffect, useMemo, useState } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import { TuragPublicHeader } from '@/components/landings/TuragLogo'
import type { PublicRoomType } from '@/lib/public-landing'
import { formatMoney } from '@/lib/money'
import { publicSiteBasePath } from '@/lib/public-landing'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api'

function tomorrowISO() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

function plusDaysISO(start: string, days: number) {
  const d = new Date(`${start}T12:00:00`)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export default function PublicBookPage() {
  const params = useParams()
  const search = useSearchParams()
  const subdomain = (params.subdomain as string) || ''
  const isTurag = subdomain.toLowerCase() === 'turag'
  const basePath =
    typeof window !== 'undefined'
      ? publicSiteBasePath(subdomain, { host: window.location.hostname })
      : `/site/${subdomain}`
  const presetType = search.get('room_type') || ''

  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<any>(null)
  const [error, setError] = useState('')
  const [roomTypes, setRoomTypes] = useState<PublicRoomType[]>([])
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    check_in: tomorrowISO(),
    check_out: plusDaysISO(tomorrowISO(), 2),
    guests: 2,
    room_type_id: presetType,
    notes: '',
  })

  const selected = roomTypes.find((r) => String(r.id) === String(form.room_type_id))
  const nights = useMemo(() => {
    if (!form.check_in || !form.check_out) return 0
    const a = new Date(`${form.check_in}T14:00:00`)
    const b = new Date(`${form.check_out}T12:00:00`)
    return Math.max(Math.round((b.getTime() - a.getTime()) / 86400000), 0)
  }, [form.check_in, form.check_out])
  const estimate = selected && nights > 0 ? Number(selected.base_rate || 0) * nights : 0

  const loadStays = async (checkIn: string, checkOut: string) => {
    setLoading(true)
    setError('')
    try {
      const res = await axios.get(`${API_BASE}/public/${subdomain}/stays`, {
        params: { check_in: checkIn, check_out: checkOut },
      })
      const types: PublicRoomType[] = res.data.room_types || []
      setRoomTypes(types)
      setForm((prev) => {
        if (prev.room_type_id && types.some((t) => String(t.id) === String(prev.room_type_id))) {
          return prev
        }
        const firstOpen = types.find((t) => (t.available_rooms ?? 1) > 0) || types[0]
        return { ...prev, room_type_id: firstOpen ? String(firstOpen.id) : '' }
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Rooms are unavailable right now')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (form.check_in && form.check_out) loadStays(form.check_in, form.check_out)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subdomain, form.check_in, form.check_out])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const res = await axios.post(`${API_BASE}/public/${subdomain}/booking`, {
        ...form,
        room_type_id: Number(form.room_type_id),
      })
      setDone(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Booking failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={`min-h-screen ${isTurag ? 'bg-[#f3f0e8] text-[#1c2e28]' : 'bg-stone-50 text-slate-900'}`}>
      {isTurag ? (
        <TuragPublicHeader
          subdomain={subdomain}
          basePath={basePath}
          right={
            <Link href={`${basePath}/order`} className="text-sm text-[#2d6a5a] hover:underline">
              Order dining
            </Link>
          }
        />
      ) : (
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
            <Link href={basePath || '/'} className="text-sm font-medium">
              ← {subdomain}
            </Link>
            <Link href={`${basePath}/order`} className="text-sm text-amber-800 hover:underline">
              Order food
            </Link>
          </div>
        </header>
      )}
      <div className="mx-auto max-w-3xl px-4 py-10">
        {isTurag && (
          <Link href={basePath || '/'} className="text-sm text-[#2d6a5a] hover:underline">
            ← Back to home
          </Link>
        )}
        <h1
          className={`mt-3 text-3xl font-semibold ${isTurag ? 'text-[#16352d]' : 'text-slate-900'}`}
          style={isTurag ? { fontFamily: 'Georgia, serif' } : undefined}
        >
          Book your stay
        </h1>
        <p className={`mt-1 text-sm ${isTurag ? 'text-[#5d6f68]' : 'text-slate-600'}`}>
          Live availability from the front desk. Your reservation is confirmed instantly.
        </p>

        {done ? (
          <div className="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6">
            <h2 className="text-lg font-medium text-emerald-900">Stay confirmed</h2>
            <p className="mt-2 text-sm text-emerald-800">{done.message}</p>
            <dl className="mt-4 grid gap-2 text-sm text-emerald-950 sm:grid-cols-2">
              <div>
                <dt className="text-emerald-700">Reference</dt>
                <dd className="font-semibold">{done.reference || done.booking?.reservation_number}</dd>
              </div>
              <div>
                <dt className="text-emerald-700">Room</dt>
                <dd>
                  {done.booking?.room_type} · {done.booking?.room_number}
                </dd>
              </div>
              <div>
                <dt className="text-emerald-700">Dates</dt>
                <dd>
                  {String(done.booking?.check_in || '').slice(0, 10)} → {String(done.booking?.check_out || '').slice(0, 10)}
                </dd>
              </div>
              <div>
                <dt className="text-emerald-700">Total</dt>
                <dd>{formatMoney(done.booking?.total_amount || 0)}</dd>
              </div>
            </dl>
            <Link
              href={basePath || '/'}
              className={`mt-4 inline-block hover:underline ${isTurag ? 'text-[#2d6a5a]' : 'text-indigo-600'}`}
            >
              Return to site
            </Link>
          </div>
        ) : (
          <form
            onSubmit={submit}
            className={`mt-8 space-y-4 border p-6 shadow-sm ${
              isTurag ? 'border-[#d9d2c4] bg-white' : 'rounded-xl border bg-white'
            }`}
          >
            {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Check-in</span>
                <input
                  required
                  type="date"
                  className="w-full rounded-lg border px-3 py-2"
                  value={form.check_in}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      check_in: e.target.value,
                      check_out: f.check_out <= e.target.value ? plusDaysISO(e.target.value, 1) : f.check_out,
                    }))
                  }
                />
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Check-out</span>
                <input
                  required
                  type="date"
                  className="w-full rounded-lg border px-3 py-2"
                  value={form.check_out}
                  onChange={(e) => setForm({ ...form, check_out: e.target.value })}
                />
              </label>
            </div>

            <div className="space-y-2">
              <p className="text-sm text-slate-600">Room type {loading ? '· checking…' : ''}</p>
              {roomTypes.length === 0 && !loading && (
                <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
                  No rooms are listed for these dates. Try different nights or contact the property.
                </p>
              )}
              <div className="grid gap-2">
                {roomTypes.map((rt) => {
                  const open = (rt.available_rooms ?? 0) > 0
                  return (
                    <label
                      key={rt.id}
                      className={`flex cursor-pointer items-start justify-between gap-3 rounded-xl border p-3 ${
                        String(form.room_type_id) === String(rt.id) ? 'border-emerald-700 bg-emerald-50' : 'border-slate-200'
                      } ${open ? '' : 'opacity-50'}`}
                    >
                      <span className="flex items-start gap-3">
                        <input
                          type="radio"
                          name="room_type"
                          className="mt-1"
                          disabled={!open}
                          checked={String(form.room_type_id) === String(rt.id)}
                          onChange={() => setForm({ ...form, room_type_id: String(rt.id) })}
                        />
                        <span>
                          <span className="block font-medium">{rt.name}</span>
                          <span className="block text-xs text-slate-500">
                            {rt.description || `Sleeps ${rt.max_occupancy}`} · {rt.available_rooms ?? 0} left
                          </span>
                        </span>
                      </span>
                      <span className="text-sm font-semibold">{formatMoney(rt.base_rate || 0, { digits: 0 })}/night</span>
                    </label>
                  )
                })}
              </div>
            </div>

            <input
              required
              className="w-full rounded-lg border px-3 py-2 text-sm"
              placeholder="Full name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                required
                className="rounded-lg border px-3 py-2 text-sm"
                placeholder="Email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              <input
                required
                className="rounded-lg border px-3 py-2 text-sm"
                placeholder="Phone"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>
            <label className="block text-sm">
              <span className="mb-1 block text-slate-600">Guests</span>
              <input
                type="number"
                min={1}
                className="w-full rounded-lg border px-3 py-2"
                value={form.guests}
                onChange={(e) => setForm({ ...form, guests: Number(e.target.value) })}
              />
            </label>
            <textarea
              className="w-full rounded-lg border px-3 py-2 text-sm"
              rows={3}
              placeholder="Special requests"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
            {nights > 0 && selected && (
              <p className="rounded-lg bg-slate-50 px-3 py-2 text-sm">
                {nights} night{nights === 1 ? '' : 's'} · estimated {formatMoney(estimate)} (pay at the property)
              </p>
            )}
            <button
              type="submit"
              disabled={saving || !form.room_type_id}
              className={`w-full rounded-full px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50 ${
                isTurag ? 'bg-[#16352d] hover:bg-[#1f4339]' : 'rounded-lg bg-slate-900 hover:bg-slate-800'
              }`}
            >
              {saving ? 'Confirming…' : 'Confirm reservation'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
