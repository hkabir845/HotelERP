'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Follow-Up Comments"
      subtitle="Notes against leads, customers, or tasks."
      endpoint="/crm/comments"
      fields={[
        { key: 'related_kind', label: 'Related to' },
        { key: 'related_name', label: 'Lead / customer' },
        { key: 'body', label: 'Comment', type: 'textarea', required: true },
      ]}
      columns={[
        { key: 'created_at', label: 'When' },
        { key: 'related_kind', label: 'Type' },
        { key: 'related_name', label: 'Related' },
        { key: 'body', label: 'Comment' },
        { key: 'created_by', label: 'By' },
      ]}
    />
  )
}
