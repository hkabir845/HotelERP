'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Message templates"
      subtitle="Reusable SMS / in-app copy for broadcast messages."
      endpoint="/catalog"
      query="?kind=broadcast_templates"
      extraBody={{ kind: 'broadcast_templates' }}
      fields={[
        { key: 'name', label: 'Template name', required: true },
        { key: 'code', label: 'Channel (sms / in_app)' },
        { key: 'notes', label: 'Message body', type: 'textarea', required: true },
      ]}
      columns={[
        { key: 'name', label: 'Template' },
        { key: 'code', label: 'Channel' },
        { key: 'notes', label: 'Body' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
