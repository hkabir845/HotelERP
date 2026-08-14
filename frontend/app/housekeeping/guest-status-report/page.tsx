'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/housekeeping"
      kind="guest-status"
      title="Guest Status Report"
      subtitle="In-house guests with room, HK status, and folio due."
      hideDates
    />
  )
}
