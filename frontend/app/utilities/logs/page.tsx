'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/utilities"
      kind="activity-log"
      title="Activity Log"
      subtitle="Staff actions recorded on the audit trail."
    />
  )
}
