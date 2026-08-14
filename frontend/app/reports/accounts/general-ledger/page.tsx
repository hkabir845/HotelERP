'use client'
import AccountReportPage from '@/components/AccountReportPage'
export default function Page() {
  return <AccountReportPage kind="general-ledger" title="General Ledger" subtitle="Movements and running balance for one account, or all accounts if none selected." needsAccount />
}
