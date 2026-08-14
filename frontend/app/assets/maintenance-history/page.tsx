'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/assets"
      kind="maintenance-history"
      title="Maintenance History"
      subtitle="Completed maintenance requests and work performed."
      hideDates
    />
  )
}
