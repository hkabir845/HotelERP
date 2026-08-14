'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Hall room"
      subtitle="Meeting / hall bookings. Full banquet events live under Banquet."
      kind="hall"
      fields={[
        { key: 'guest_name', label: 'Organizer', required: true },
        { key: 'item', label: 'Hall / event', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'guest_name', label: 'Organizer' },
        { key: 'item', label: 'Hall / event' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
