'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/crm/reports"
      kind="guest-frequency"
      title="Guest Frequency Report"
      subtitle="How often each guest stayed in the period."
    />
  )
}
