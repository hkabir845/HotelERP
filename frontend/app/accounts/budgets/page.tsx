'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
import { COA } from '@/lib/coaDefaults'
export default function Page() {
  return (
    <RecordWorkbench
      title="Budgets"
      subtitle="Period budgets by ledger account — expense budget defaults to General Operating (6920)."
      endpoint="/accounts/budgets"
      fields={[
        { key: 'name', label: 'Budget name', required: true },
        {
          key: 'account_id',
          label: 'Account',
          type: 'select',
          optionsKey: 'accounts',
          required: true,
          suggestCode: COA.GENERAL_OPEX,
          recommendHint: true,
        },
        { key: 'period_start', label: 'From', type: 'date', required: true },
        { key: 'period_end', label: 'To', type: 'date', required: true },
        { key: 'budgeted_amount', label: 'Amount', type: 'number', required: true },
        { key: 'description', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'name', label: 'Budget' },
        { key: 'account_name', label: 'Account' },
        { key: 'period_start', label: 'From' },
        { key: 'period_end', label: 'To' },
        { key: 'budgeted_amount', label: 'Budgeted' },
        { key: 'actual_amount', label: 'Actual' },
        { key: 'variance', label: 'Variance' },
      ]}
    />
  )
}
