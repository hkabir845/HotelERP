'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="purchase"
      title="Purchase Report"
      subtitle="Posted purchases and returns in the selected period."
    />
  )
}
