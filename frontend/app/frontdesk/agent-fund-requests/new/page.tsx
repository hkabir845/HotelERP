'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="New Agent Fund Request"
      subtitle="Request an advance or payout for a booking agent."
      endpoint="/frontdesk/agent-funds"
      createLabel="Submit request"
      fields={[
        { key: 'agent_id', label: 'Agent', type: 'select', optionsKey: 'agents', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'request_date', label: 'Date', type: 'date' },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'request_number', label: 'No.' },
        { key: 'agent_name', label: 'Agent' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
