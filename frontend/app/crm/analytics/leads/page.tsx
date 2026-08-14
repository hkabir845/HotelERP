'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/crm/reports"
      kind="leads"
      title="Lead Analytics"
      subtitle="Leads by source with pipeline value."
    />
  )
}
