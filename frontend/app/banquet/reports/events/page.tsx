'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/banquet/reports"
      kind="events"
      title="Event Report"
      subtitle="Banquet events in the period with venue, pax, folio total, and due."
    />
  )
}
