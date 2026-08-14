'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Payment List"
      subtitle="Payroll slips that have been paid."
      endpoint="/hr/payroll"
      query="?paid=1"
      fields={[]}
      columns={[
        { key: 'pay_date', label: 'Paid on' },
        { key: 'payroll_number', label: 'Payroll' },
        { key: 'employee_name', label: 'Employee' },
        { key: 'payment_method', label: 'Method' },
        { key: 'net_pay', label: 'Net' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
