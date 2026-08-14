'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/crm/reports"
      kind="checklists"
      title="Checklist Report"
      subtitle="Open tasks and lead follow-ups still due."
      hideDates
    />
  )
}
