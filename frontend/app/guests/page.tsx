'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Guest list"
      subtitle="Customer details — profiles, ID, and loyalty for the property."
      endpoint="/guests"
      fields={[
        { key: 'first_name', label: 'First name', required: true },
        { key: 'last_name', label: 'Last name' },
        { key: 'email', label: 'Email', type: 'email' },
        { key: 'phone', label: 'Phone' },
        { key: 'nationality', label: 'Nationality' },
        { key: 'id_number', label: 'ID number' },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'phone', label: 'Phone' },
        { key: 'nationality', label: 'Nationality' },
        { key: 'id_number', label: 'ID' },
        { key: 'is_vip', label: 'VIP' },
      ]}
    />
  )
}
