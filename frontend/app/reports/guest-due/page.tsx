'use client'
import FrontdeskReportPage from '@/components/FrontdeskReportPage'
export default function Page() {
  return <FrontdeskReportPage kind="guest-due" title="Guest Due Report" subtitle="Open folio balances on in-house, confirmed, and checked-out stays." hideDates />
}
