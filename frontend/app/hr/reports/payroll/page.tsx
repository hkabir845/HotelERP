'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/hr/reports"
      kind="payroll"
      title="Payroll Report"
      subtitle="Payroll slips whose period overlaps the selected dates."
    />
  )
}
