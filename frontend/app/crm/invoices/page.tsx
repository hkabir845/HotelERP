'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Invoice"
      subtitle="CRM invoices with collect and void."
      endpoint="/crm/invoices"
      fields={[
        { key: 'customer_id', label: 'Customer', type: 'select', optionsKey: 'customers' },
        { key: 'customer_name', label: 'Customer name', required: true },
        { key: 'phone', label: 'Phone' },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'due_date', label: 'Due date', type: 'date' },
        { key: 'notes', label: 'Description', type: 'textarea' },
      ]}
      columns={[
        { key: 'number', label: 'Invoice' },
        { key: 'customer_name', label: 'Customer' },
        { key: 'due_date', label: 'Due date' },
        { key: 'amount', label: 'Amount' },
        { key: 'paid_amount', label: 'Paid' },
        { key: 'due', label: 'Due' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'pay', label: 'Collect', flag: 'can_pay', tone: 'emerald' },
        { id: 'void', label: 'Void', flag: 'can_void', tone: 'red' },
      ]}
      payAction="pay"
    />
  )
}
