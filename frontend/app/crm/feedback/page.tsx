'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Guest Feedback"
      subtitle="Capture ratings and close the loop."
      endpoint="/crm/feedback"
      fields={[
        { key: 'guest_name', label: 'Guest', required: true },
        { key: 'place', label: 'Room / outlet' },
        { key: 'rating', label: 'Rating (1-5)', type: 'number', required: true },
        { key: 'comments', label: 'Comments', type: 'textarea' },
      ]}
      columns={[
        { key: 'guest_name', label: 'Guest' },
        { key: 'place', label: 'Place' },
        { key: 'rating', label: 'Rating' },
        { key: 'status', label: 'Status' },
        { key: 'comments', label: 'Comments' },
      ]}
      actions={[
        { id: 'review', label: 'In review', flag: 'can_review' },
        { id: 'resolve', label: 'Resolved', flag: 'can_resolve', tone: 'emerald' },
      ]}
    />
  )
}
