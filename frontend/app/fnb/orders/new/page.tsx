'use client'

import { useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { hasModule } from '@/lib/modules'
import { useRouter } from 'next/navigation'
import {
  UtensilsCrossed,
  Plus,
  Minus,
  Search,
  Loader2,
  ShoppingCart,
  Trash2,
  CheckCircle2,
  CreditCard,
  Banknote,
  Receipt,
  RotateCcw,
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface MenuItem {
  id: number
  name: string
  description: string | null
  price: number
  category: string
  image_url: string | null
}

interface OrderItem {
  menu_item_id: number
  name: string
  quantity: number
  price: number
  subtotal: number
}

type OrderType = 'dine_in' | 'takeaway' | 'room' | 'pos'
type PayMethod = 'cash' | 'card' | 'room_charge' | 'later'

export default function NewOrderPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const enabledModules = (user?.enabled_modules || user?.tenant?.enabled_modules || []) as string[]
  const canRoomService = hasModule(enabledModules, 'frontdesk')

  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [orderItems, setOrderItems] = useState<OrderItem[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [orderType, setOrderType] = useState<OrderType>('dine_in')
  const [tableNumber, setTableNumber] = useState('')
  const [roomNumber, setRoomNumber] = useState('')
  const [customerName, setCustomerName] = useState('Walk-in')
  const [customerPhone, setCustomerPhone] = useState('')
  const [paymentMethod, setPaymentMethod] = useState<PayMethod>('cash')
  const [notes, setNotes] = useState('')
  const [ticketNo, setTicketNo] = useState<string | null>(null)
  const [posCustomers, setPosCustomers] = useState<{ id: number; name: string; phone?: string }[]>([])
  const [revenueCenters, setRevenueCenters] = useState<{ id: number; name: string }[]>([])
  const [posCustomerId, setPosCustomerId] = useState('')
  const [revenueCenter, setRevenueCenter] = useState('')

  const categories = useMemo(
    () => Array.from(new Set(menuItems.map((item) => item.category))),
    [menuItems]
  )

  useEffect(() => {
    fetchMenuItems()
    apiClient.get('/fnb/config/pos-customers').then((res) => setPosCustomers(res.data.items || [])).catch(() => {})
    apiClient.get('/fnb/config/revenue-centers').then((res) => {
      const items = res.data.items || []
      setRevenueCenters(items)
      if (items[0]?.name) setRevenueCenter(items[0].name)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!canRoomService && orderType === 'room') {
      setOrderType('dine_in')
    }
  }, [canRoomService, orderType])

  const fetchMenuItems = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/fnb/menu-items')
      setMenuItems(response.data.items || [])
    } catch {
      setMenuItems([])
    } finally {
      setLoading(false)
    }
  }

  const addToOrder = (item: MenuItem) => {
    setOrderItems((prev) => {
      const existing = prev.find((oi) => oi.menu_item_id === item.id)
      if (existing) {
        return prev.map((oi) =>
          oi.menu_item_id === item.id
            ? { ...oi, quantity: oi.quantity + 1, subtotal: (oi.quantity + 1) * oi.price }
            : oi
        )
      }
      return [
        ...prev,
        {
          menu_item_id: item.id,
          name: item.name,
          quantity: 1,
          price: item.price,
          subtotal: item.price,
        },
      ]
    })
  }

  const updateQuantity = (menuItemId: number, delta: number) => {
    setOrderItems((prev) =>
      prev
        .map((item) => {
          if (item.menu_item_id !== menuItemId) return item
          const quantity = Math.max(0, item.quantity + delta)
          return { ...item, quantity, subtotal: quantity * item.price }
        })
        .filter((item) => item.quantity > 0)
    )
  }

  const removeItem = (menuItemId: number) => {
    setOrderItems((prev) => prev.filter((item) => item.menu_item_id !== menuItemId))
  }

  const clearCart = () => {
    setOrderItems([])
    setNotes('')
    setTicketNo(null)
  }

  const subtotal = orderItems.reduce((sum, item) => sum + item.subtotal, 0)
  const tax = Math.round(subtotal * 0.1 * 100) / 100
  const total = Math.round((subtotal + tax) * 100) / 100

  const filteredItems = menuItems.filter((item) => {
    const q = searchTerm.toLowerCase()
    const matchesSearch =
      !q ||
      item.name.toLowerCase().includes(q) ||
      item.description?.toLowerCase().includes(q)
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const resetAfterSuccess = () => {
    setOrderItems([])
    setNotes('')
    setTableNumber('')
    setRoomNumber('')
    setCustomerName('Walk-in')
    setCustomerPhone('')
    setPosCustomerId('')
    setTicketNo(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (orderItems.length === 0) return
    if (orderType === 'room' && !roomNumber.trim()) {
      alert('Room number is required for room service')
      return
    }
    if (orderType === 'dine_in' && !tableNumber.trim()) {
      alert('Table number is required for dine-in')
      return
    }

    setSubmitting(true)
    setTicketNo(null)

    try {
      const apiOrderType =
        orderType === 'dine_in' ? 'pos' : orderType === 'pos' ? 'pos' : orderType

      const payload = {
        order_type: apiOrderType,
        room_number: orderType === 'room' ? roomNumber : null,
        table_number: orderType === 'dine_in' ? tableNumber : null,
        customer_name: customerName || 'Walk-in',
        customer_phone: customerPhone || null,
        pos_customer_id: posCustomerId || null,
        revenue_center: revenueCenter || null,
        payment_method: paymentMethod,
        items: orderItems.map((item) => ({
          menu_item_id: item.menu_item_id,
          quantity: item.quantity,
          price: item.price,
        })),
        subtotal,
        tax,
        total,
        notes,
      }

      const res = await apiClient.post('/fnb/orders', payload)
      const created = res.data || {}
      const order = created.order || created
      const low = order.low_stock_after_order || []
      if (low.length) {
        alert(
          `Order placed. Kitchen stock is low after this ticket: ${low.map((m: any) => m.name).join(', ')}`
        )
      }
      const ticket =
        order.order_number ||
        created.order_number ||
        order.ticket_no ||
        order.id ||
        `T-${Date.now().toString().slice(-6)}`
      setTicketNo(String(ticket))

      setTimeout(() => {
        resetAfterSuccess()
        if (orderType === 'room') {
          router.push('/fnb/orders/active-room-wise')
        } else {
          router.push('/fnb/orders/active')
        }
      }, 1600)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create order')
    } finally {
      setSubmitting(false)
    }
  }

  const typeBtn = (key: OrderType, label: string) => (
    <button
      key={key}
      type="button"
      onClick={() => setOrderType(key)}
      className={`min-h-[48px] flex-1 rounded-xl px-3 py-3 text-sm font-semibold transition ${
        orderType === key
          ? 'bg-emerald-700 text-white shadow'
          : 'bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50'
      }`}
    >
      {label}
    </button>
  )

  const payBtn = (key: PayMethod, label: string, Icon: any) => (
    <button
      key={key}
      type="button"
      onClick={() => setPaymentMethod(key)}
      className={`flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-xl px-2 py-2 text-xs font-semibold sm:text-sm ${
        paymentMethod === key
          ? 'bg-slate-900 text-white'
          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
      }`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  )

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-stone-100">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-hidden">
          <form onSubmit={handleSubmit} className="flex h-full flex-col">
            <header className="flex flex-wrap items-center justify-between gap-3 border-b bg-white px-5 py-3">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-emerald-100 p-2">
                  <UtensilsCrossed className="h-6 w-6 text-emerald-800" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900">Restaurant POS</h1>
                  <p className="text-xs text-slate-500">Touch-friendly order entry</p>
                </div>
              </div>
              <div className="flex min-w-[280px] flex-1 gap-2 sm:max-w-md">
                {typeBtn('dine_in', 'Dine-in')}
                {typeBtn('takeaway', 'Takeaway')}
                {canRoomService && typeBtn('room', 'Room')}
              </div>
            </header>

            {ticketNo && (
              <div className="mx-5 mt-3 flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-900">
                <CheckCircle2 className="h-5 w-5 shrink-0" />
                <div>
                  <p className="font-semibold">Order placed</p>
                  <p className="text-sm">Ticket / order #: {ticketNo}</p>
                </div>
              </div>
            )}

            <div className="grid min-h-0 flex-1 grid-cols-1 gap-0 lg:grid-cols-[1fr_380px]">
              {/* Menu pane */}
              <section className="flex min-h-0 flex-col overflow-hidden p-4">
                <div className="mb-3 flex flex-wrap gap-2">
                  {(orderType === 'dine_in' || orderType === 'takeaway') && (
                    <>
                      {orderType === 'dine_in' && (
                        <input
                          value={tableNumber}
                          onChange={(e) => setTableNumber(e.target.value)}
                          placeholder="Table #"
                          className="w-28 rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium"
                          required
                        />
                      )}
                      <input
                        value={customerName}
                        onChange={(e) => setCustomerName(e.target.value)}
                        placeholder="Guest name"
                        className="min-w-[140px] flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm"
                      />
                      <input
                        value={customerPhone}
                        onChange={(e) => setCustomerPhone(e.target.value)}
                        placeholder="Phone"
                        className="w-36 rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm"
                      />
                      {posCustomers.length > 0 && (
                        <select
                          value={posCustomerId}
                          onChange={(e) => {
                            const id = e.target.value
                            setPosCustomerId(id)
                            const row = posCustomers.find((c) => String(c.id) === id)
                            if (row) {
                              setCustomerName(row.name)
                              if (row.phone) setCustomerPhone(row.phone)
                            }
                          }}
                          className="min-w-[160px] rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm"
                        >
                          <option value="">POS customer</option>
                          {posCustomers.map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.name}
                            </option>
                          ))}
                        </select>
                      )}
                      {revenueCenters.length > 0 && (
                        <select
                          value={revenueCenter}
                          onChange={(e) => setRevenueCenter(e.target.value)}
                          className="min-w-[140px] rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm"
                        >
                          {revenueCenters.map((c) => (
                            <option key={c.id} value={c.name}>
                              {c.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </>
                  )}
                  {orderType === 'room' && (
                    <input
                      value={roomNumber}
                      onChange={(e) => setRoomNumber(e.target.value)}
                      placeholder="Room number"
                      className="w-40 rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium"
                      required
                    />
                  )}
                </div>

                <div className="mb-3 flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <input
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search menu..."
                      className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-9 pr-3 text-sm"
                    />
                  </div>
                </div>

                <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
                  <button
                    type="button"
                    onClick={() => setSelectedCategory('all')}
                    className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium ${
                      selectedCategory === 'all'
                        ? 'bg-slate-900 text-white'
                        : 'bg-white text-slate-700 ring-1 ring-slate-200'
                    }`}
                  >
                    All
                  </button>
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setSelectedCategory(cat)}
                      className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium ${
                        selectedCategory === cat
                          ? 'bg-slate-900 text-white'
                          : 'bg-white text-slate-700 ring-1 ring-slate-200'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>

                <div className="min-h-0 flex-1 overflow-y-auto rounded-2xl bg-white p-3 ring-1 ring-slate-200">
                  {loading ? (
                    <div className="flex h-48 items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin text-emerald-700" />
                    </div>
                  ) : filteredItems.length === 0 ? (
                    <div className="flex h-48 items-center justify-center text-sm text-slate-500">
                      No menu items found
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
                      {filteredItems.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => addToOrder(item)}
                          className="flex min-h-[110px] flex-col items-start rounded-2xl border border-slate-200 bg-stone-50 p-3 text-left transition hover:border-emerald-600 hover:bg-emerald-50 active:scale-[0.98]"
                        >
                          <span className="line-clamp-2 text-sm font-semibold text-slate-900">
                            {item.name}
                          </span>
                          <span className="mt-auto pt-2 text-lg font-bold text-emerald-800">
                            {formatMoney(item.price)}
                          </span>
                          <span className="text-[11px] uppercase tracking-wide text-slate-400">
                            {item.category}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </section>

              {/* Cart pane */}
              <aside className="flex min-h-0 flex-col border-l border-slate-200 bg-white">
                <div className="flex items-center justify-between border-b px-4 py-3">
                  <h2 className="flex items-center gap-2 font-semibold text-slate-900">
                    <ShoppingCart className="h-5 w-5 text-emerald-700" />
                    Cart ({orderItems.reduce((n, i) => n + i.quantity, 0)})
                  </h2>
                  <button
                    type="button"
                    onClick={clearCart}
                    disabled={!orderItems.length}
                    className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-slate-600 hover:bg-slate-100 disabled:opacity-40"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    Clear
                  </button>
                </div>

                <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
                  {orderItems.length === 0 ? (
                    <div className="flex h-full flex-col items-center justify-center text-slate-400">
                      <Receipt className="mb-2 h-10 w-10" />
                      <p className="text-sm">Tap items to add</p>
                    </div>
                  ) : (
                    orderItems.map((item) => (
                      <div
                        key={item.menu_item_id}
                        className="rounded-xl bg-stone-50 p-3 ring-1 ring-slate-200"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <div className="truncate text-sm font-medium text-slate-900">
                              {item.name}
                            </div>
                            <div className="text-xs text-slate-500">
                              {formatMoney(item.price)} each
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeItem(item.menu_item_id)}
                            className="rounded p-1 text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                        <div className="mt-2 flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() => updateQuantity(item.menu_item_id, -1)}
                              className="flex h-9 w-9 items-center justify-center rounded-lg bg-white ring-1 ring-slate-300"
                            >
                              <Minus className="h-4 w-4" />
                            </button>
                            <span className="w-8 text-center text-sm font-bold">
                              {item.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => updateQuantity(item.menu_item_id, 1)}
                              className="flex h-9 w-9 items-center justify-center rounded-lg bg-white ring-1 ring-slate-300"
                            >
                              <Plus className="h-4 w-4" />
                            </button>
                          </div>
                          <div className="text-sm font-semibold">
                            {formatMoney(item.subtotal)}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="space-y-3 border-t p-4">
                  <div className="flex gap-2">
                    {payBtn('cash', 'Cash', Banknote)}
                    {payBtn('card', 'Card', CreditCard)}
                    {canRoomService &&
                      orderType === 'room' &&
                      payBtn('room_charge', 'Room', Receipt)}
                    {payBtn('later', 'Later', Receipt)}
                  </div>

                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={2}
                    placeholder="Kitchen notes..."
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />

                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between text-slate-600">
                      <span>Subtotal</span>
                      <span>{formatMoney(subtotal)}</span>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Tax (10%)</span>
                      <span>{formatMoney(tax)}</span>
                    </div>
                    <div className="flex justify-between text-lg font-bold text-slate-900">
                      <span>Total</span>
                      <span className="text-emerald-800">{formatMoney(total)}</span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={submitting || orderItems.length === 0}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-700 px-4 py-4 text-base font-semibold text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="h-5 w-5" />
                        Place order · {formatMoney(total)}
                      </>
                    )}
                  </button>
                </div>
              </aside>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  )
}
