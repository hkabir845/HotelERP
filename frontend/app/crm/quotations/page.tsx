'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Quotation"
      subtitle="Draft → send → accept → make invoice, or reject."
      endpoint="/crm/quotations"
      fields={[
        { key: 'customer_id', label: 'Customer', type: 'select', optionsKey: 'customers' },
        { key: 'customer_name', label: 'Customer name', required: true },
        { key: 'phone', label: 'Phone' },
        { key: 'company', label: 'Company' },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'valid_until', label: 'Valid until', type: 'date' },
        { key: 'notes', label: 'Scope', type: 'textarea' },
      ]}
      columns={[
        { key: 'number', label: 'Quote' },
        { key: 'customer_name', label: 'Customer' },
        { key: 'amount', label: 'Amount' },
        { key: 'valid_until', label: 'Valid until' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'send', label: 'Send', flag: 'can_send' },
        { id: 'accept', label: 'Accept', flag: 'can_accept', tone: 'emerald' },
        { id: 'invoice', label: 'Make invoice', flag: 'can_invoice' },
        { id: 'reject', label: 'Reject', flag: 'can_reject', tone: 'red' },
      ]}
    />
  )
}
