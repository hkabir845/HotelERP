'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Pool booking"
      subtitle="Book pool slots for in-house and walk-in guests."
      kind="pool"
      fields={[
        { key: 'guest_name', label: 'Guest', required: true },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Package', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'guest_name', label: 'Guest' },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Package' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
