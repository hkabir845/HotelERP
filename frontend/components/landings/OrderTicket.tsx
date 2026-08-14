'use client'

import { formatMoney } from '@/lib/money'

type TicketItem = { name: string; price: number; quantity: number; category?: string }

export type OrderTicketKind = 'kot' | 'guest' | 'invoice'

export type OrderTicketData = {
  companyName: string
  logo?: string | null
  phone?: string
  address?: string
  email?: string
  customerName: string
  customerPhone: string
  notes: string
  serveWhere: 'restaurant' | 'room'
  tableLabel?: string
  roomNumber?: string
  requestedAt: string
  items: TicketItem[]
  subtotal: number
  tax: number
  total: number
  orderNumber?: string
  paymentStatus?: string
  guestKind?: string
}

export default function OrderTicket({
  data,
  kind = 'kot',
}: {
  data: OrderTicketData
  kind?: OrderTicketKind
}) {
  const isKot = kind === 'kot'
  const serveLabel =
    data.serveWhere === 'room'
      ? `Room ${data.roomNumber || '—'}`
      : data.tableLabel || 'Restaurant'
  const when = data.requestedAt ? new Date(data.requestedAt).toLocaleString() : '—'
  const punched = new Date().toLocaleString()
  const heading = isKot ? 'KOT' : kind === 'invoice' ? 'Invoice' : 'Guest bill'
  const docNo = data.orderNumber
    ? `${isKot ? 'KOT' : kind === 'invoice' ? 'INV' : 'BILL'}-${data.orderNumber}`
    : punched

  return (
    <div className="order-ticket mx-auto bg-white text-black" style={{ width: '80mm', maxWidth: '100%', padding: '16px' }}>
      <div className="text-center">
        {data.logo ? (
          <img
            src={data.logo}
            alt={data.companyName}
            className="mx-auto mb-2 h-14 w-auto max-w-[180px] object-contain"
          />
        ) : null}
        <h1 className="text-base font-semibold leading-tight">{data.companyName}</h1>
        {data.address ? <p className="mt-1 text-[11px] leading-snug">{data.address}</p> : null}
        {data.phone ? <p className="text-[11px]">Tel: {data.phone}</p> : null}
        {data.email ? <p className="text-[11px]">{data.email}</p> : null}
      </div>

      <div className="my-2 border-t border-dashed border-black" />

      <p className="text-center text-sm font-semibold">{heading}</p>
      {data.orderNumber ? <p className="text-center text-[11px] font-semibold">{docNo}</p> : null}
      <p className="text-center text-[11px]">{punched}</p>

      <div className="my-2 border-t border-dashed border-black" />

      <div className="space-y-0.5 text-xs">
        <p>Guest: {data.customerName || '—'}</p>
        <p>Phone: {data.customerPhone || '—'}</p>
        <p>Serve: {serveLabel}</p>
        <p>Time: {when}</p>
        {data.orderNumber ? <p>Order: {data.orderNumber}</p> : null}
        {data.guestKind ? <p>Guest: {data.guestKind.replace('_', ' ')}</p> : null}
        {data.paymentStatus ? (
          <p>
            Payment:{' '}
            {data.paymentStatus === 'paid'
              ? 'Paid'
              : data.paymentStatus === 'room_charge'
                ? 'Charged to room'
                : 'Unpaid'}
          </p>
        ) : null}
      </div>

      <div className="my-2 border-t border-dashed border-black" />

      {isKot ? (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-black/20 text-left">
              <th className="py-1">Qty</th>
              <th className="py-1">Item</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item, idx) => (
              <tr key={`${item.name}-${idx}`}>
                <td className="w-10 py-1 align-top font-semibold">{item.quantity}×</td>
                <td className="py-1">{item.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-black/20 text-left">
              <th className="py-1">Item</th>
              <th className="py-1 text-right">Qty</th>
              <th className="py-1 text-right">Amt</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item, idx) => (
              <tr key={`${item.name}-${idx}`}>
                <td className="py-1 pr-2">{item.name}</td>
                <td className="py-1 text-right">{item.quantity}</td>
                <td className="py-1 text-right">{formatMoney(item.price * item.quantity)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {data.notes ? (
        <p className="mt-2 text-xs">
          <span className="font-semibold">Notes:</span> {data.notes}
        </p>
      ) : null}

      {isKot ? (
        <p className="mt-3 text-center text-[11px]">Kitchen copy · not a bill</p>
      ) : (
        <>
          <div className="my-2 border-t border-dashed border-black" />
          <div className="space-y-0.5 text-xs">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{formatMoney(data.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Tax</span>
              <span>{formatMoney(data.tax)}</span>
            </div>
            <div className="flex justify-between text-sm font-semibold">
              <span>Total</span>
              <span>{formatMoney(data.total)}</span>
            </div>
          </div>
          <p className="mt-3 text-center text-[11px]">Thank you. Please present this ticket at service.</p>
        </>
      )}
    </div>
  )
}
