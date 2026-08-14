'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
import { COA } from '@/lib/coaDefaults'
export default function Page() {
  return (
    <RecordWorkbench
      title="AR receipts"
      subtitle="Receive customer payments — settlement account auto-suggested (Bank / Cash)."
      endpoint="/accounts/receivable/payments"
      fields={[
        { key: 'receivable_id', label: 'Invoice', type: 'select', optionsKey: 'invoices', required: true },
        { key: 'payment_date', label: 'Date', type: 'date', required: true },
        { key: 'amount', label: 'Amount', type: 'number', required: true },
        { key: 'payment_method', label: 'Method' },
        {
          key: 'settlement_account_id',
          label: 'Settlement account',
          type: 'select',
          optionsKey: 'settlement_accounts',
          suggestCode: COA.BANK,
          recommendHint: true,
        },
        { key: 'reference', label: 'Reference' },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'invoice_number', label: 'Invoice' },
        { key: 'customer_name', label: 'Customer' },
        { key: 'payment_date', label: 'Date' },
        { key: 'amount', label: 'Amount' },
        { key: 'method', label: 'Method' },
        { key: 'reference', label: 'Reference' },
      ]}
    />
  )
}
