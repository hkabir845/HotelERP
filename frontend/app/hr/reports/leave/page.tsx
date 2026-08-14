'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/hr/reports"
      kind="leave"
      title="Employee Leave Report"
      subtitle="Leave requests overlapping the selected dates."
    />
  )
}
