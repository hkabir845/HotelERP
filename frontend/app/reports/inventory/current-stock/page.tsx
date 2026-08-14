'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="current-stock"
      title="Current Stock"
      subtitle="On-hand quantity and value by item and warehouse."
      hideDates
    />
  )
}
