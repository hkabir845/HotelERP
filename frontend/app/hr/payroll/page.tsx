'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Payroll Management"
      subtitle="Generate slips from salary structure and attendance late fines, then approve and pay."
      endpoint="/hr/payroll"
      generateLabel="Generate"
      fields={[
        { key: 'pay_period_start', label: 'Period start', type: 'date', required: true },
        { key: 'pay_period_end', label: 'Period end', type: 'date', required: true },
        { key: 'employee_id', label: 'Employee (blank = all active)', type: 'select', optionsKey: 'employees' },
      ]}
      columns={[
        { key: 'payroll_number', label: 'Payroll' },
        { key: 'employee_name', label: 'Employee' },
        { key: 'pay_period_start', label: 'From' },
        { key: 'pay_period_end', label: 'To' },
        { key: 'gross_pay', label: 'Gross' },
        { key: 'total_deductions', label: 'Deductions' },
        { key: 'net_pay', label: 'Net' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'approve', label: 'Approve', flag: 'can_approve' },
        { id: 'pay', label: 'Pay', flag: 'can_pay', tone: 'emerald' },
        { id: 'cancel', label: 'Cancel', flag: 'can_cancel', tone: 'red' },
      ]}
      payAction="pay"
    />
  )
}
