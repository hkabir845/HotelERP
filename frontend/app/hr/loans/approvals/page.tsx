'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Loan Approvals"
      subtitle="Pending staff loan requests waiting for approval."
      endpoint="/hr/loans"
      query="?pending=1"
      fields={[]}
      columns={[
        { key: 'number', label: 'No.' },
        { key: 'employee_name', label: 'Employee' },
        { key: 'amount', label: 'Amount' },
        { key: 'installments', label: 'Installments' },
        { key: 'purpose', label: 'Purpose' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'approve', label: 'Approve', flag: 'can_approve', tone: 'emerald' },
        { id: 'reject', label: 'Reject', flag: 'can_reject', tone: 'red' },
      ]}
    />
  )
}
