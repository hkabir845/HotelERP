'use client'
import FrontdeskReportPage from '@/components/FrontdeskReportPage'
export default function Page() {
  return <FrontdeskReportPage kind="inhouse-summary" title="Inhouse Summary" subtitle="Currently checked-in rooms by type, with due balances." hideDates />
}
