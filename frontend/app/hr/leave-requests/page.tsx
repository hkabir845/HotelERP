'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Leave Requests"
      subtitle="Staff leave: submit, then approve or reject."
      endpoint="/hr/leaves"
      fields={[
        { key: 'employee_id', label: 'Employee', type: 'select', optionsKey: 'employees', required: true },
        { key: 'leave_type_id', label: 'Leave type', type: 'select', optionsKey: 'leave_types', required: true },
        { key: 'date_from', label: 'From', type: 'date', required: true },
        { key: 'date_to', label: 'To', type: 'date', required: true },
        { key: 'days', label: 'Days', type: 'number' },
        { key: 'reason', label: 'Reason', type: 'textarea' },
      ]}
      columns={[
        { key: 'employee_name', label: 'Employee' },
        { key: 'leave_type', label: 'Type' },
        { key: 'date_from', label: 'From' },
        { key: 'date_to', label: 'To' },
        { key: 'days', label: 'Days' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'approve', label: 'Approve', flag: 'can_approve', tone: 'emerald' },
        { id: 'reject', label: 'Reject', flag: 'can_reject', tone: 'red' },
      ]}
    />
  )
}
