'use client'

import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import { CreditCard, Eye, Lock, Minus, Plus, Printer, ShoppingCart, Wallet, X } from 'lucide-react'
import { TuragPublicHeader } from '@/components/landings/TuragLogo'
import TuragLogo from '@/components/landings/TuragLogo'
import OrderTicket, { type OrderTicketData, type OrderTicketKind } from '@/components/landings/OrderTicket'
import { TURAG_CONTENT } from '@/lib/landings/turag-content'
import type { PublicLanding, PublicMenuItem, PublicRoom, PublicTable } from '@/lib/public-landing'
import { publicSiteBasePath } from '@/lib/public-landing'
import { formatMoney } from '@/lib/money'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api'

function defaultServeTime() {
  const d = new Date()
  d.setMinutes(d.getMinutes() + 45)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

type GuestKind = 'residential' | 'booking' | 'arrival' | 'meal_only'
type PayMethod = 'card' | 'wallet'

export default function PublicOrderPage() {
  const params = useParams()
  const subdomain = params.subdomain as string
  const isTurag = subdomain?.toLowerCase() === 'turag'
  const basePath =
    typeof window !== 'undefined'
      ? publicSiteBasePath(subdomain, { host: window.location.hostname })
      : `/site/${subdomain}`
  const [items, setItems] = useState<PublicMenuItem[]>([])
  const [tables, setTables] = useState<PublicTable[]>([])
  const [rooms, setRooms] = useState<PublicRoom[]>([])
  const [canRoom, setCanRoom] = useState(false)
  const [hasStay, setHasStay] = useState(false)
  const [cart, setCart] = useState<Record<number, number>>({})
  const [category, setCategory] = useState('all')
  const [customerName, setCustomerName] = useState('')
  const [customerPhone, setCustomerPhone] = useState('')
  const [customerEmail, setCustomerEmail] = useState('')
  const [notes, setNotes] = useState('')
  const [guestKind, setGuestKind] = useState<GuestKind>('meal_only')
  const [bookingRef, setBookingRef] = useState('')
  const [serveWhere, setServeWhere] = useState<'restaurant' | 'room'>('restaurant')
  const [tableId, setTableId] = useState('')
  const [roomNumber, setRoomNumber] = useState('')
  const [requestedAt, setRequestedAt] = useState(defaultServeTime)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [done, setDone] = useState<any>(null)
  const [error, setError] = useState('')
  const [company, setCompany] = useState<PublicLanding | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [ticket, setTicket] = useState<OrderTicketData | null>(null)
  const [ticketKind, setTicketKind] = useState<OrderTicketKind>('kot')
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [payMethod, setPayMethod] = useState<PayMethod>('card')
  const [cardNumber, setCardNumber] = useState('')
  const [cardExpiry, setCardExpiry] = useState('')
  const [cardCvc, setCardCvc] = useState('')
  const [walletNumber, setWalletNumber] = useState('')
  const [paying, setPaying] = useState(false)

  useEffect(() => {
    axios
      .get(`${API_BASE}/public/${subdomain}/menu`)
      .then((res) => {
        setItems(res.data.items || [])
        setTables(res.data.tables || [])
        setRooms(res.data.rooms || [])
        const fulfillment: string[] = res.data.fulfillment || ['restaurant']
        const roomOk = fulfillment.includes('room') && (res.data.rooms || []).length > 0
        setCanRoom(roomOk)
        setHasStay((res.data.guest_kinds || []).includes('residential'))
        if (!roomOk) setServeWhere('restaurant')
      })
      .catch((err) => setError(err.response?.data?.detail || 'Menu unavailable'))
      .finally(() => setLoading(false))

    axios
      .get(`${API_BASE}/public/landing/${subdomain}`)
      .then((res) => setCompany(res.data))
      .catch(() => setCompany(null))
  }, [subdomain])

  const categories = useMemo(() => Array.from(new Set(items.map((i) => i.category))), [items])
  const visible = items.filter((i) => category === 'all' || i.category === category)
  const cartItems = items
    .filter((i) => cart[i.id])
    .map((i) => ({
      menu_item_id: i.id,
      name: i.name,
      price: i.price,
      quantity: cart[i.id],
      category: i.category,
    }))
  const subtotal = cartItems.reduce((s, i) => s + i.price * i.quantity, 0)
  const tax = subtotal * 0.1
  const total = subtotal + tax

  const tableLabel = tables.find((t) => String(t.id) === String(tableId))
    ? `Table ${tables.find((t) => String(t.id) === String(tableId))?.table_number}`
    : ''

  const companyName = company?.landing_title || company?.name || (isTurag ? TURAG_CONTENT.brand : subdomain)
  const companyLogo = company?.logo || (isTurag ? TURAG_CONTENT.images.logo : null)
  const companyPhone = company?.phone || (isTurag ? TURAG_CONTENT.contact.phones[0] : '')
  const companyAddress =
    company?.address ||
    [company?.city, company?.country].filter(Boolean).join(', ') ||
    (isTurag ? TURAG_CONTENT.contact.resortAddress : '')
  const companyEmail = company?.email || (isTurag ? TURAG_CONTENT.contact.emails[0] : '')

  const buildTicket = (orderNumber?: string): OrderTicketData => ({
    companyName,
    logo: companyLogo,
    phone: companyPhone || undefined,
    address: companyAddress || undefined,
    email: companyEmail || undefined,
    customerName,
    customerPhone,
    notes,
    serveWhere,
    tableLabel,
    roomNumber,
    requestedAt,
    items: cartItems,
    subtotal,
    tax,
    total,
    orderNumber,
    guestKind,
    paymentStatus: done?.order?.payment_status,
  })

  const paid = Boolean(
    done?.order?.print_allowed ||
      done?.order?.payment_status === 'paid' ||
      done?.order?.payment_status === 'room_charge'
  )
  const stayGuest = guestKind !== 'meal_only'

  const openPreview = (orderNumber?: string, kind: OrderTicketKind = 'kot') => {
    if (cartItems.length === 0 && !ticket) return
    const next = cartItems.length ? buildTicket(orderNumber) : ticket
    if (!next) return
    setTicket(next)
    setTicketKind(kind)
    setPreviewOpen(true)
  }

  const requirePaidThen = (action: () => void) => {
    if (paid) {
      action()
      return
    }
    startCheckout()
  }

  const printTicket = (kind: OrderTicketKind = 'kot') => {
    requirePaidThen(() => {
      if (cartItems.length) setTicket(buildTicket(ticket?.orderNumber || done?.order?.order_number))
      setTicketKind(kind)
      setPreviewOpen(true)
      window.setTimeout(() => window.print(), 80)
    })
  }

  const add = (id: number) => setCart((c) => ({ ...c, [id]: (c[id] || 0) + 1 }))
  const dec = (id: number) =>
    setCart((c) => {
      const next = { ...c }
      if (!next[id]) return next
      next[id] -= 1
      if (next[id] <= 0) delete next[id]
      return next
    })
  const clearOrder = () => {
    setCart({})
    setCustomerName('')
    setCustomerPhone('')
    setCustomerEmail('')
    setNotes('')
    setTableId('')
    setRoomNumber('')
    setBookingRef('')
    setGuestKind('meal_only')
    setServeWhere('restaurant')
    setRequestedAt(defaultServeTime())
    setError('')
    setDone(null)
    setCheckoutOpen(false)
  }

  const orderPayload = () => ({
    customer_name: customerName,
    customer_phone: customerPhone,
    customer_email: customerEmail,
    items: cartItems,
    notes,
    guest_kind: guestKind,
    serve_where: guestKind === 'meal_only' ? 'restaurant' : serveWhere,
    table_id: serveWhere === 'restaurant' && tableId ? Number(tableId) : undefined,
    room_number: serveWhere === 'room' || guestKind === 'residential' ? roomNumber : undefined,
    reservation_number: bookingRef || undefined,
    requested_at: requestedAt ? new Date(requestedAt).toISOString() : undefined,
    payment_method: stayGuest ? 'room_charge' : undefined,
  })

  const startCheckout = async () => {
    if (!customerName || cartItems.length === 0) {
      setError('Add items and your name before checkout')
      return
    }
    if (guestKind === 'meal_only' && serveWhere === 'room') {
      setError('Meal-only orders are served at the restaurant after online payment')
      return
    }
    if (serveWhere === 'room' && !roomNumber && guestKind === 'residential') {
      setError('Choose the room for delivery')
      return
    }
    if ((guestKind === 'booking' || guestKind === 'arrival') && !bookingRef) {
      setError('Enter your booking confirmation number')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (stayGuest) {
        const res = await axios.post(`${API_BASE}/public/${subdomain}/order`, orderPayload())
        setDone(res.data)
        const confirmed = buildTicket(res.data?.order?.order_number)
        setTicket({ ...confirmed, paymentStatus: res.data?.order?.payment_status, guestKind })
        setTicketKind('invoice')
        setPreviewOpen(true)
        setCart({})
        return
      }
      const res = await axios.post(`${API_BASE}/public/${subdomain}/order`, {
        ...orderPayload(),
        payment_method: 'gateway',
      })
      setDone(res.data)
      setCheckoutOpen(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not start checkout')
    } finally {
      setSaving(false)
    }
  }

  const completePayment = async () => {
    const checkoutRef = done?.order?.checkout_ref
    if (!checkoutRef) {
      setError('Start checkout first')
      return
    }
    setPaying(true)
    setError('')
    try {
      const res = await axios.post(`${API_BASE}/public/${subdomain}/order/pay`, {
        checkout_ref: checkoutRef,
        payment_method: payMethod,
        card_number: payMethod === 'card' ? cardNumber : undefined,
        card_expiry: cardExpiry,
        card_cvc: cardCvc,
        wallet_number: payMethod === 'wallet' ? walletNumber : undefined,
        customer_email: customerEmail,
      })
      setDone(res.data)
      setCheckoutOpen(false)
      const confirmed = buildTicket(res.data?.order?.order_number)
      setTicket({ ...confirmed, paymentStatus: 'paid', guestKind })
      setTicketKind('invoice')
      setPreviewOpen(true)
      setCart({})
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Payment failed')
    } finally {
      setPaying(false)
    }
  }

  const submit = async () => {
    await startCheckout()
  }

  return (
    <div className={`min-h-screen ${isTurag ? 'bg-[#f3f0e8]' : 'bg-orange-50'}`}>
      {isTurag ? (
        <TuragPublicHeader
          subdomain={subdomain}
          basePath={basePath}
          right={
            <Link href={`${basePath}/book`} className="text-sm text-[#2d6a5a] hover:underline">
              Book a stay
            </Link>
          }
        />
      ) : (
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <Link href={basePath || '/'} className="text-sm font-medium">
              ← {subdomain}
            </Link>
            <Link href={`${basePath}/book`} className="text-sm text-amber-800 hover:underline">
              Book a stay
            </Link>
          </div>
        </header>
      )}
      <div className="mx-auto max-w-6xl px-4 py-8">
        {isTurag && (
          <Link href={basePath || '/'} className="text-sm text-[#2d6a5a] hover:underline">
            ← Back to home
          </Link>
        )}
        <h1 className={`mt-2 text-3xl font-semibold ${isTurag ? 'text-[#16352d]' : 'text-slate-900'}`}>
          Order food
        </h1>
        <p className="text-sm text-slate-600">
          Order from the restaurant, your room (in-house, booking, or arrival), or as a meal-only guest.
          Preview is free. Print and checkout need payment — stay guests can charge the room; meal-only guests pay online.
        </p>

        {done && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            {isTurag && <TuragLogo heightClass="h-16" className="mb-2" />}
            {done.message} · Order <strong>{done.order?.order_number}</strong> · Total{' '}
            {formatMoney(done.order?.total || 0)}
            {done.order?.payment_status === 'pending' && (
              <span> · Payment required to confirm and print</span>
            )}
          </div>
        )}
        {error && <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_340px]">
          <div>
            <div className="mb-4 flex flex-wrap gap-2">
              <button
                onClick={() => setCategory('all')}
                className={`rounded-full px-3 py-1 text-sm ${category === 'all' ? 'bg-slate-900 text-white' : 'bg-white border'}`}
              >
                All
              </button>
              {categories.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategory(c)}
                  className={`rounded-full px-3 py-1 text-sm ${category === c ? 'bg-slate-900 text-white' : 'bg-white border'}`}
                >
                  {c}
                </button>
              ))}
            </div>
            {loading ? (
              <div className="rounded-xl border bg-white p-8 text-center text-slate-500">Loading menu...</div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {visible.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => add(item.id)}
                    className="rounded-xl border bg-white p-4 text-left shadow-sm hover:border-orange-400"
                  >
                    <div className="font-medium text-slate-900">{item.name}</div>
                    <div className="mt-1 line-clamp-2 text-xs text-slate-500">{item.description}</div>
                    <div className="mt-3 text-lg font-semibold text-orange-600">{formatMoney(item.price)}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <aside className="h-fit rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="flex items-center justify-between gap-2 font-medium">
              <span className="flex items-center gap-2">
                <ShoppingCart className="h-4 w-4" /> Your order
              </span>
              <button
                type="button"
                onClick={clearOrder}
                className="inline-flex min-h-[36px] min-w-[36px] items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:border-red-200 hover:bg-red-50 hover:text-red-600"
                aria-label="Clear order"
                title="Clear / cancel order"
              >
                <X className="h-4 w-4" />
              </button>
            </h2>
            <div className="mt-3 space-y-2">
              {cartItems.length === 0 && <p className="text-sm text-slate-500">Tap menu items to add</p>}
              {cartItems.map((item) => (
                <div key={item.menu_item_id} className="flex items-center justify-between rounded-lg bg-slate-50 p-2 text-sm">
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-slate-500">{formatMoney(item.price)}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button type="button" onClick={() => dec(item.menu_item_id)} className="rounded border p-1">
                      <Minus className="h-3 w-3" />
                    </button>
                    <span>{item.quantity}</span>
                    <button type="button" onClick={() => add(item.menu_item_id)} className="rounded border p-1">
                      <Plus className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-2 border-t pt-3 text-sm">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>{formatMoney(subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span>Tax</span>
                <span>{formatMoney(tax)}</span>
              </div>
              <div className="flex justify-between font-semibold">
                <span>Total</span>
                <span>{formatMoney(total)}</span>
              </div>
            </div>

            <p className="mt-4 text-xs font-medium uppercase tracking-wide text-slate-500">Who is ordering</p>
            <div className="mt-2 grid grid-cols-2 gap-2">
              {(
                [
                  ['meal_only', 'Meal only · pay online'],
                  ['residential', 'Residential guest'],
                  ['booking', 'Booking confirmation'],
                  ['arrival', 'Arriving today'],
                ] as [GuestKind, string][]
              )
                .filter(([key]) => key === 'meal_only' || hasStay)
                .map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => {
                      setGuestKind(key)
                      if (key === 'meal_only') setServeWhere('restaurant')
                      if (key === 'residential') setServeWhere('room')
                    }}
                    className={`rounded-lg border px-3 py-2 text-left text-xs ${
                      guestKind === key ? 'border-emerald-700 bg-emerald-50 font-medium' : ''
                    }`}
                  >
                    {label}
                  </button>
                ))}
            </div>

            <p className="mt-4 text-xs font-medium uppercase tracking-wide text-slate-500">Serve where</p>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setServeWhere('restaurant')}
                className={`rounded-lg border px-3 py-2 text-sm ${
                  serveWhere === 'restaurant' ? 'border-emerald-700 bg-emerald-50 font-medium' : ''
                }`}
              >
                At restaurant
              </button>
              <button
                type="button"
                disabled={!canRoom}
                onClick={() => {
                  setServeWhere('room')
                  if (guestKind === 'meal_only') setGuestKind('residential')
                }}
                className={`rounded-lg border px-3 py-2 text-sm disabled:opacity-40 ${
                  serveWhere === 'room' ? 'border-emerald-700 bg-emerald-50 font-medium' : ''
                }`}
              >
                To my room
              </button>
            </div>

            {serveWhere === 'restaurant' ? (
              <select
                className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
                value={tableId}
                onChange={(e) => setTableId(e.target.value)}
              >
                <option value="">Any table / host will seat</option>
                {tables.map((t) => (
                  <option key={t.id} value={t.id}>
                    Table {t.table_number} · {t.capacity} seats {t.location ? `· ${t.location}` : ''}
                  </option>
                ))}
              </select>
            ) : (
              <select
                className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
                value={roomNumber}
                onChange={(e) => setRoomNumber(e.target.value)}
              >
                <option value="">Select room</option>
                {rooms.map((r) => (
                  <option key={r.id} value={r.room_number}>
                    Room {r.room_number}
                    {r.room_type ? ` · ${r.room_type}` : ''}
                  </option>
                ))}
              </select>
            )}

            {(guestKind === 'booking' || guestKind === 'arrival' || guestKind === 'residential') && (
              <input
                className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
                placeholder={
                  guestKind === 'residential'
                    ? 'Booking reference (optional)'
                    : 'Booking confirmation number'
                }
                value={bookingRef}
                onChange={(e) => setBookingRef(e.target.value)}
              />
            )}

            <label className="mt-2 block text-sm">
              <span className="mb-1 block text-slate-600">Serve / delivery time</span>
              <input
                type="datetime-local"
                className="w-full rounded-lg border px-3 py-2 text-sm"
                value={requestedAt}
                onChange={(e) => setRequestedAt(e.target.value)}
                required
              />
            </label>

            <input
              className="mt-3 w-full rounded-lg border px-3 py-2 text-sm"
              placeholder="Your name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
            <input
              className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
              placeholder="Phone"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
            />
            <input
              className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
              placeholder="Email (receipt)"
              type="email"
              value={customerEmail}
              onChange={(e) => setCustomerEmail(e.target.value)}
            />
            <textarea
              className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
              rows={2}
              placeholder="Notes for the kitchen"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <div className="mt-3 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => openPreview(undefined, 'kot')}
                disabled={cartItems.length === 0 && !ticket}
                className="inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                <Eye className="h-4 w-4" />
                Preview KOT
              </button>
              <button
                type="button"
                onClick={() => openPreview(undefined, 'invoice')}
                disabled={cartItems.length === 0 && !ticket}
                className="inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                <Eye className="h-4 w-4" />
                Preview invoice
              </button>
              <button
                type="button"
                onClick={() => printTicket('kot')}
                disabled={cartItems.length === 0 && !ticket}
                className="inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                {paid ? <Printer className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                Print KOT
              </button>
              <button
                type="button"
                onClick={() => printTicket('invoice')}
                disabled={cartItems.length === 0 && !ticket}
                className="inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                {paid ? <Printer className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                Print invoice
              </button>
              <button
                type="button"
                onClick={clearOrder}
                className="inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border border-slate-300 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <X className="h-4 w-4" />
                Clear
              </button>
              <button
                type="button"
                onClick={submit}
                disabled={saving || !customerName || cartItems.length === 0}
                className={`min-h-[44px] rounded-lg py-2.5 text-sm font-medium text-white disabled:opacity-50 ${
                  isTurag ? 'bg-[#16352d] hover:bg-[#1f4339]' : 'bg-orange-600 hover:bg-orange-500'
                }`}
              >
                {saving
                  ? 'Please wait...'
                  : stayGuest
                    ? 'Charge to room & confirm'
                    : 'Checkout & pay'}
              </button>
            </div>
          </aside>
        </div>
      </div>

      {previewOpen && ticket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 print:static print:bg-white print:p-0">
          <div className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-xl bg-white shadow-xl print:max-h-none print:max-w-none print:shadow-none">
            <div className="flex items-center justify-between border-b px-4 py-3 print:hidden">
              <p className="font-medium">
                {ticketKind === 'kot' ? 'KOT' : ticketKind === 'invoice' ? 'Invoice' : 'Guest bill'}
              </p>
              <div className="flex items-center gap-2">
                <div className="flex rounded-lg border text-xs">
                  <button
                    type="button"
                    onClick={() => setTicketKind('kot')}
                    className={`px-2 py-1 ${ticketKind === 'kot' ? 'bg-slate-900 text-white' : ''}`}
                  >
                    KOT
                  </button>
                  <button
                    type="button"
                    onClick={() => setTicketKind('invoice')}
                    className={`px-2 py-1 ${ticketKind === 'invoice' ? 'bg-slate-900 text-white' : ''}`}
                  >
                    Invoice
                  </button>
                  <button
                    type="button"
                    onClick={() => setTicketKind('guest')}
                    className={`px-2 py-1 ${ticketKind === 'guest' ? 'bg-slate-900 text-white' : ''}`}
                  >
                    Bill
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => setPreviewOpen(false)}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-full border"
                  aria-label="Close preview"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div id="order-print-root">
              <OrderTicket data={ticket} kind={ticketKind} />
            </div>
            <div className="flex gap-2 border-t p-4 print:hidden">
              <button
                type="button"
                onClick={() => requirePaidThen(() => window.print())}
                className={`inline-flex flex-1 items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-medium text-white ${
                  isTurag ? 'bg-[#16352d]' : 'bg-slate-900'
                }`}
              >
                {paid ? <Printer className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                {paid ? `Print ${ticketKind === 'kot' ? 'KOT' : ticketKind === 'invoice' ? 'invoice' : 'bill'}` : 'Pay to print'}
              </button>
              <button
                type="button"
                onClick={() => setPreviewOpen(false)}
                className="flex-1 rounded-lg border py-2.5 text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {checkoutOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4 print:hidden">
          <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
            <div className="flex items-center justify-between border-b px-4 py-3">
              <div>
                <p className="font-medium">Secure checkout</p>
                <p className="text-xs text-slate-500">Ecommerce payment · {done?.order?.order_number || 'new order'}</p>
              </div>
              <button
                type="button"
                onClick={() => setCheckoutOpen(false)}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border"
                aria-label="Close checkout"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="space-y-3 p-4 text-sm">
              <div className="rounded-lg bg-slate-50 p-3">
                <div className="flex justify-between">
                  <span>Items</span>
                  <span>{cartItems.length || ticket?.items.length || 0}</span>
                </div>
                <div className="mt-1 flex justify-between font-semibold">
                  <span>Total due</span>
                  <span>{formatMoney(done?.order?.total || total)}</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setPayMethod('card')}
                  className={`inline-flex items-center justify-center gap-1 rounded-lg border px-3 py-2 ${
                    payMethod === 'card' ? 'border-emerald-700 bg-emerald-50 font-medium' : ''
                  }`}
                >
                  <CreditCard className="h-4 w-4" /> Card
                </button>
                <button
                  type="button"
                  onClick={() => setPayMethod('wallet')}
                  className={`inline-flex items-center justify-center gap-1 rounded-lg border px-3 py-2 ${
                    payMethod === 'wallet' ? 'border-emerald-700 bg-emerald-50 font-medium' : ''
                  }`}
                >
                  <Wallet className="h-4 w-4" /> bKash / Nagad
                </button>
              </div>
              {payMethod === 'card' ? (
                <>
                  <input
                    className="w-full rounded-lg border px-3 py-2"
                    placeholder="Card number"
                    inputMode="numeric"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      className="rounded-lg border px-3 py-2"
                      placeholder="MM/YY"
                      value={cardExpiry}
                      onChange={(e) => setCardExpiry(e.target.value)}
                    />
                    <input
                      className="rounded-lg border px-3 py-2"
                      placeholder="CVC"
                      value={cardCvc}
                      onChange={(e) => setCardCvc(e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-slate-500">Demo gateway — use any 13+ digit card. 4000000000000002 declines.</p>
                </>
              ) : (
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  placeholder="Mobile wallet number"
                  inputMode="numeric"
                  value={walletNumber}
                  onChange={(e) => setWalletNumber(e.target.value)}
                />
              )}
              <button
                type="button"
                onClick={completePayment}
                disabled={paying}
                className={`flex w-full min-h-[44px] items-center justify-center gap-2 rounded-lg py-2.5 font-medium text-white disabled:opacity-50 ${
                  isTurag ? 'bg-[#16352d]' : 'bg-orange-600'
                }`}
              >
                <Lock className="h-4 w-4" />
                {paying ? 'Processing…' : `Pay ${formatMoney(done?.order?.total || total)}`}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @media print {
          body * { visibility: hidden; }
          #order-print-root, #order-print-root * { visibility: visible; }
          #order-print-root {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
