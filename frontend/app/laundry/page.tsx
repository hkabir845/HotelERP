'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Laundry POS"
      subtitle="Guest laundry tickets — charge to room or settle at desk."
      kind="laundry"
      fields={[
        { key: 'guest_name', label: 'Guest', required: true },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Item', required: true },
        { key: 'quantity', label: 'Qty', type: 'number', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ticket' },
        { key: 'guest_name', label: 'Guest' },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Item' },
        { key: 'quantity', label: 'Qty' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
