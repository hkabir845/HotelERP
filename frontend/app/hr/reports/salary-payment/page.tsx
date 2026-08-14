'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/hr/reports"
      kind="salary-payment"
      title="Salary Payment Report"
      subtitle="Paid payroll slips in the period."
    />
  )
}
