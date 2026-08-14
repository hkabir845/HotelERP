'use client'
import AccountReportPage from '@/components/AccountReportPage'
export default function Page() {
  return <AccountReportPage kind="group-ledger" title="Group Ledger" subtitle="Roll-up of posting accounts under a selected group." needsAccount />
}
