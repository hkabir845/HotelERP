'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="cost-of-consumption"
      title="Cost of Consumption Report"
      subtitle="Posted revenue-center and amenities issues at item cost."
    />
  )
}
