'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/banquet/reports"
      kind="items"
      title="Individual Item Report"
      subtitle="Extra banquet items billed in the period, grouped by item."
    />
  )
}
