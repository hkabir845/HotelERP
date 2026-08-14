'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/crm/reports"
      kind="guests"
      title="Guest Analytics"
      subtitle="Stays and nights by guest in the period."
    />
  )
}
