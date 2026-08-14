'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/banquet/reports"
      kind="services"
      title="Service Report"
      subtitle="Event services billed in the period, grouped by service."
    />
  )
}
