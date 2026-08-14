'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Travel desk"
      subtitle="Pickup, drop, and pre-arranged transfers."
      kind="travel"
      fields={[
        { key: 'guest_name', label: 'Guest', required: true },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Transfer', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'guest_name', label: 'Guest' },
        { key: 'room_number', label: 'Room' },
        { key: 'item', label: 'Transfer' },
        { key: 'notes', label: 'Notes' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
