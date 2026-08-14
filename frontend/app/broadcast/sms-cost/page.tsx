'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/broadcast"
      kind="sms-cost"
      title="SMS Cost Report"
      subtitle="SMS broadcasts in the period, with recipient count and unit cost."
    />
  )
}
