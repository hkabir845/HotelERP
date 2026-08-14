'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="New Broadcast Message"
      subtitle="Send an in-app announcement or SMS. SMS uses the unit cost from Additional Configs."
      endpoint="/broadcast/messages"
      createLabel="Send"
      fields={[
        { key: 'title', label: 'Subject', required: true },
        { key: 'channel', label: 'Channel', type: 'select', optionsKey: 'channels' },
        { key: 'priority', label: 'Priority', type: 'select', optionsKey: 'priorities' },
        { key: 'recipient_count', label: 'Recipients', type: 'number' },
        { key: 'message', label: 'Message', type: 'textarea', required: true },
      ]}
      columns={[
        { key: 'title', label: 'Subject' },
        { key: 'channel', label: 'Channel' },
        { key: 'recipient_count', label: 'Recipients' },
        { key: 'cost', label: 'Cost' },
        { key: 'status', label: 'Status' },
        { key: 'sent_at', label: 'Sent' },
      ]}
    />
  )
}
