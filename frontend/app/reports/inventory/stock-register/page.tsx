'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="stock-register"
      title="Stock Register"
      subtitle="In / out movements with running balance."
    />
  )
}
