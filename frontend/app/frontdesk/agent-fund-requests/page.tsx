'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Agent Fund Requests"
      subtitle="Advance / payout requests for booking agents. Approve, then mark paid."
      endpoint="/frontdesk/agent-funds"
      createLabel="Create request"
      fields={[
        { key: 'agent_id', label: 'Agent', type: 'select', optionsKey: 'agents', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'request_date', label: 'Date', type: 'date' },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'request_number', label: 'No.' },
        { key: 'agent_name', label: 'Agent' },
        { key: 'request_date', label: 'Date' },
        { key: 'amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'approve', label: 'Approve', flag: 'can_approve', tone: 'emerald' },
        { id: 'pay', label: 'Pay', flag: 'can_pay' },
        { id: 'reject', label: 'Reject', flag: 'can_reject', tone: 'red' },
      ]}
    />
  )
}
