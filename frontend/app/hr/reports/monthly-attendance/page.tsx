'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/hr/reports"
      kind="monthly-attendance"
      title="Monthly Attendance"
      subtitle="Present days, hours, and late days by employee."
    />
  )
}
