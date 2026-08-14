'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/banquet/reports"
      kind="set-menu"
      title="Set Menu Report"
      subtitle="Per-pax set menus sold on events in the period."
    />
  )
}
