'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Plus, Trash2 } from 'lucide-react'

type Opt = { id: number | string; name: string; cost_price?: number }

type Mode =
  | 'requisition'
  | 'purchase'
  | 'return'
  | 'transfer'
  | 'adjustment-add'
  | 'adjustment-remove'
  | 'consumption-rc'
  | 'consumption-amenity'
  | 'payment'

const META: Record<
  Mode,
  { title: string; subtitle: string; endpoint: string; listPath: string }
> = {
  requisition: {
    title: 'New Requisition',
    subtitle: 'Request items from store. Approve, then fulfill to issue stock.',
    endpoint: '/inventory/requisitions',
    listPath: '/inventory/requisitions',
  },
  purchase: {
    title: 'Purchase',
    subtitle: 'Receive stock from a supplier into a warehouse.',
    endpoint: '/inventory/purchases',
    listPath: '/inventory/purchases',
  },
  return: {
    title: 'Purchase Return',
    subtitle: 'Return stock to a supplier and deduct warehouse quantity.',
    endpoint: '/inventory/purchases',
    listPath: '/inventory/purchases',
  },
  transfer: {
    title: 'Warehouse Transfer',
    subtitle: 'Move stock from one warehouse to another.',
    endpoint: '/inventory/transfers',
    listPath: '/inventory/warehouse-transfers',
  },
  'adjustment-add': {
    title: 'Stock Adjustment — Add',
    subtitle: 'Increase warehouse stock (found, opening, count gain).',
    endpoint: '/inventory/adjustments',
    listPath: '/inventory/stock-adjustments',
  },
  'adjustment-remove': {
    title: 'Stock Adjustment — Remove',
    subtitle: 'Decrease warehouse stock (write-off, damage, count loss).',
    endpoint: '/inventory/adjustments',
    listPath: '/inventory/stock-adjustments',
  },
  'consumption-rc': {
    title: 'Revenue Center Consumption',
    subtitle: 'Issue stock to an F&B or other revenue center.',
    endpoint: '/inventory/consumptions',
    listPath: '/inventory/revenue-center-consumption',
  },
  'consumption-amenity': {
    title: 'Amenities Consumption',
    subtitle: 'Issue amenities from store to rooms / housekeeping.',
    endpoint: '/inventory/consumptions',
    listPath: '/inventory/amenities-consumption',
  },
  payment: {
    title: 'Supplier Payment',
    subtitle: 'Pay outstanding supplier invoices.',
    endpoint: '/inventory/payments',
    listPath: '/inventory/suppliers/payments',
  },
}

function emptyLine() {
  return { item_id: '', quantity: '', unit_price: '' }
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function InventoryDocForm({ mode }: { mode: Mode }) {
  const router = useRouter()
  const meta = META[mode]
  const [options, setOptions] = useState<Record<string, Opt[]>>({})
  const [docDate, setDocDate] = useState(today())
  const [department, setDepartment] = useState('')
  const [warehouseId, setWarehouseId] = useState('')
  const [fromWarehouseId, setFromWarehouseId] = useState('')
  const [toWarehouseId, setToWarehouseId] = useState('')
  const [supplierId, setSupplierId] = useState('')
  const [revenueCenter, setRevenueCenter] = useState('')
  const [reason, setReason] = useState('')
  const [notes, setNotes] = useState('')
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState('cash')
  const [reference, setReference] = useState('')
  const [lines, setLines] = useState([emptyLine()])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const withPrice = mode === 'purchase' || mode === 'return'
  const isPayment = mode === 'payment'

  const items = options.items || []
  const warehouses = options.warehouses || []
  const suppliers = options.suppliers || []
  const centers = options.revenue_centers || []

  useEffect(() => {
    apiClient
      .get('/inventory/config/warehouses')
      .then((res) => {
        setOptions(res.data.options || {})
        const wh = res.data.options?.warehouses || []
        if (wh[0] && !warehouseId) setWarehouseId(String(wh[0].id))
        if (wh[0] && !fromWarehouseId) setFromWarehouseId(String(wh[0].id))
        if (wh[1] && !toWarehouseId) setToWarehouseId(String(wh[1].id))
        else if (wh[0] && !toWarehouseId) setToWarehouseId(String(wh[0].id))
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load masters'))
  }, [])

  const updateLine = (index: number, key: string, value: string) => {
    setLines((prev) =>
      prev.map((line, i) => {
        if (i !== index) return line
        const next = { ...line, [key]: value }
        if (key === 'item_id') {
          const item = items.find((row) => String(row.id) === value)
          if (item && withPrice && !next.unit_price) {
            next.unit_price = String(item.cost_price || '')
          }
        }
        return next
      })
    )
  }

  const total = useMemo(() => {
    return lines.reduce((sum, line) => {
      const qty = Number(line.quantity || 0)
      const price = Number(line.unit_price || 0)
      return sum + qty * (withPrice ? price : 0)
    }, 0)
  }, [lines, withPrice])

  const payload = (post: boolean) => {
    const itemRows = lines
      .filter((l) => l.item_id && Number(l.quantity) > 0)
      .map((l) => ({
        item_id: Number(l.item_id),
        quantity: Number(l.quantity),
        unit_price: Number(l.unit_price || 0),
      }))
    if (mode === 'requisition') {
      return {
        requested_date: docDate,
        department,
        warehouse_id: warehouseId,
        notes,
        items: itemRows,
        post,
      }
    }
    if (mode === 'purchase' || mode === 'return') {
      return {
        purchase_date: docDate,
        supplier_id: supplierId,
        warehouse_id: warehouseId,
        is_return: mode === 'return',
        notes,
        items: itemRows,
        post,
      }
    }
    if (mode === 'transfer') {
      return {
        transfer_date: docDate,
        from_warehouse_id: fromWarehouseId,
        to_warehouse_id: toWarehouseId,
        notes,
        items: itemRows,
        post,
      }
    }
    if (mode === 'adjustment-add' || mode === 'adjustment-remove') {
      return {
        adjustment_date: docDate,
        adjustment_type: mode === 'adjustment-add' ? 'add' : 'remove',
        warehouse_id: warehouseId,
        reason,
        notes,
        items: itemRows,
        post,
      }
    }
    if (mode === 'consumption-rc' || mode === 'consumption-amenity') {
      return {
        consumption_date: docDate,
        kind: mode === 'consumption-amenity' ? 'amenities' : 'revenue_center',
        warehouse_id: warehouseId,
        revenue_center: revenueCenter,
        notes,
        items: itemRows,
        post,
      }
    }
    return {
      payment_date: docDate,
      supplier_id: supplierId,
      amount,
      method,
      reference,
      notes,
    }
  }

  const submit = async (post: boolean) => {
    setSaving(true)
    setError('')
    try {
      const body = payload(post)
      if (!isPayment && !(body as any).items?.length) {
        throw new Error('Add at least one item')
      }
      await apiClient.post(meta.endpoint, body)
      router.push(meta.listPath)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const warehouseSelect = (
    label: string,
    value: string,
    onChange: (v: string) => void
  ) => (
    <label className="text-sm">
      <span className="mb-1 block text-slate-600">{label}</span>
      <select
        required
        className="w-full rounded-lg border px-3 py-2"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Select…</option>
        {warehouses.map((w) => (
          <option key={w.id} value={w.id}>
            {w.name}
          </option>
        ))}
      </select>
    </label>
  )

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{meta.title}</h1>
          <p className="mt-1 text-gray-600">{meta.subtitle}</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Date</span>
              <input
                type="date"
                className="w-full rounded-lg border px-3 py-2"
                value={docDate}
                onChange={(e) => setDocDate(e.target.value)}
              />
            </label>
            {mode === 'requisition' && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Department</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                />
              </label>
            )}
            {(mode === 'purchase' || mode === 'return' || isPayment) && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Supplier</span>
                <select
                  required
                  className="w-full rounded-lg border px-3 py-2"
                  value={supplierId}
                  onChange={(e) => setSupplierId(e.target.value)}
                >
                  <option value="">Select…</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {mode === 'transfer' ? (
              <>
                {warehouseSelect('From warehouse', fromWarehouseId, setFromWarehouseId)}
                {warehouseSelect('To warehouse', toWarehouseId, setToWarehouseId)}
              </>
            ) : (
              !isPayment && warehouseSelect('Warehouse', warehouseId, setWarehouseId)
            )}
            {(mode === 'adjustment-add' || mode === 'adjustment-remove') && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Reason</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </label>
            )}
            {mode === 'consumption-rc' && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Revenue center</span>
                <select
                  className="w-full rounded-lg border px-3 py-2"
                  value={revenueCenter}
                  onChange={(e) => setRevenueCenter(e.target.value)}
                >
                  <option value="">Select…</option>
                  {centers.map((c) => (
                    <option key={String(c.id)} value={c.name}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {mode === 'consumption-amenity' && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Amenity / area</span>
                <input
                  className="w-full rounded-lg border px-3 py-2"
                  value={revenueCenter}
                  onChange={(e) => setRevenueCenter(e.target.value)}
                  placeholder="Rooms, floor, amenity name"
                />
              </label>
            )}
            {isPayment && (
              <>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Amount</span>
                  <input
                    type="number"
                    step="0.01"
                    required
                    className="w-full rounded-lg border px-3 py-2"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Method</span>
                  <select
                    className="w-full rounded-lg border px-3 py-2"
                    value={method}
                    onChange={(e) => setMethod(e.target.value)}
                  >
                    {(options.payment_methods || []).map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Reference</span>
                  <input
                    className="w-full rounded-lg border px-3 py-2"
                    value={reference}
                    onChange={(e) => setReference(e.target.value)}
                  />
                </label>
              </>
            )}
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Notes</span>
              <input
                className="w-full rounded-lg border px-3 py-2"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </label>
          </div>

          {!isPayment && (
            <div className="mt-4 overflow-auto rounded-xl border bg-white">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Item</th>
                    <th className="px-3 py-2 w-28">Qty</th>
                    {withPrice && <th className="px-3 py-2 w-32">Unit price</th>}
                    {withPrice && <th className="px-3 py-2 w-32 text-right">Line</th>}
                    <th className="px-3 py-2 w-12" />
                  </tr>
                </thead>
                <tbody>
                  {lines.map((line, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-3 py-2">
                        <select
                          className="w-full rounded border px-2 py-1"
                          value={line.item_id}
                          onChange={(e) => updateLine(idx, 'item_id', e.target.value)}
                        >
                          <option value="">Select item…</option>
                          {items.map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="px-3 py-2">
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          className="w-full rounded border px-2 py-1"
                          value={line.quantity}
                          onChange={(e) => updateLine(idx, 'quantity', e.target.value)}
                        />
                      </td>
                      {withPrice && (
                        <td className="px-3 py-2">
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            className="w-full rounded border px-2 py-1"
                            value={line.unit_price}
                            onChange={(e) => updateLine(idx, 'unit_price', e.target.value)}
                          />
                        </td>
                      )}
                      {withPrice && (
                        <td className="px-3 py-2 text-right">
                          {formatMoney(Number(line.quantity || 0) * Number(line.unit_price || 0))}
                        </td>
                      )}
                      <td className="px-3 py-2">
                        <button
                          type="button"
                          onClick={() => setLines((prev) => prev.filter((_, i) => i !== idx))}
                          className="text-red-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex items-center justify-between border-t px-3 py-3">
                <button
                  type="button"
                  onClick={() => setLines((prev) => [...prev, emptyLine()])}
                  className="inline-flex items-center gap-1 text-sm text-indigo-700"
                >
                  <Plus className="h-4 w-4" />
                  Add line
                </button>
                {withPrice && <div className="font-semibold">Total {formatMoney(total)}</div>}
              </div>
            </div>
          )}

          <div className="mt-4 flex gap-2">
            <button
              type="button"
              disabled={saving}
              onClick={() => submit(false)}
              className="rounded-lg border bg-white px-4 py-2 text-sm disabled:opacity-50"
            >
              {isPayment ? 'Save' : 'Save draft'}
            </button>
            {!isPayment && (
              <button
                type="button"
                disabled={saving}
                onClick={() => submit(true)}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
              >
                Save & post
              </button>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
