'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Spa & beauty salon"
      subtitle="Appointments, therapists, and guest wellness charges."
      kind="spa"
      fields={[
        { key: 'guest_name', label: 'Guest', required: true },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Service', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'notes', label: 'Therapist / notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'guest_name', label: 'Guest' },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Service' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
