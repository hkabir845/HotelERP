'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      kind="guest-status"
      title="F&B Guest Status Report"
      subtitle="In-house guests with F&B orders posted to their room or stay."
      hideDates
    />
  )
}
