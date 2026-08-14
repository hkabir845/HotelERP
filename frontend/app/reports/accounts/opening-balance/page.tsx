'use client'
import AccountReportPage from '@/components/AccountReportPage'
export default function Page() {
  return (
    <AccountReportPage
      kind="opening-balance"
      title="Opening Balance Report"
      subtitle="Opening balances with as-of date and linked opening journals (vs Opening Balance Equity)."
    />
  )
}
