'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="inventory"
      title="Inventory Report"
      subtitle="Opening, receipts, issues, and closing stock for the period."
    />
  )
}
