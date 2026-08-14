'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Channel manager"
      subtitle="OTA / channel connections for rates and availability."
      endpoint="/channels"
      fields={[
        { key: 'channel_name', label: 'Channel (Booking.com, Agoda…)', required: true },
        { key: 'property_code', label: 'Property code' },
        { key: 'notes', label: 'Notes', type: 'textarea' },
        { key: 'is_active', label: 'Active', type: 'checkbox' },
      ]}
      columns={[
        { key: 'channel_name', label: 'Channel' },
        { key: 'property_code', label: 'Property code' },
        { key: 'is_active', label: 'Active' },
        { key: 'notes', label: 'Notes' },
      ]}
    />
  )
}
