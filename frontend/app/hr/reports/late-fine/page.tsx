'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/hr/reports"
      kind="late-fine"
      title="Late Fine Report"
      subtitle="Late punch-ins and fines posted from HR settings / shift grace."
    />
  )
}
