'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Loan List"
      subtitle="Staff loans: request → approve → disburse → repay → close."
      endpoint="/hr/loans"
      fields={[
        { key: 'employee_id', label: 'Employee', type: 'select', optionsKey: 'employees', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'installments', label: 'Installments', type: 'number' },
        { key: 'request_date', label: 'Request date', type: 'date' },
        { key: 'purpose', label: 'Purpose', type: 'textarea' },
      ]}
      columns={[
        { key: 'number', label: 'No.' },
        { key: 'employee_name', label: 'Employee' },
        { key: 'amount', label: 'Amount' },
        { key: 'paid_amount', label: 'Paid' },
        { key: 'due', label: 'Due' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'approve', label: 'Approve', flag: 'can_approve' },
        { id: 'disburse', label: 'Disburse', flag: 'can_disburse' },
        { id: 'repay', label: 'Repay', flag: 'can_repay', tone: 'emerald' },
        { id: 'reject', label: 'Reject', flag: 'can_reject', tone: 'red' },
        { id: 'close', label: 'Close', flag: 'can_close' },
      ]}
      payAction="repay"
    />
  )
}
