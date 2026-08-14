'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="item-wise-purchase"
      title="Item Wise Purchase Summary"
      subtitle="Net purchased quantity and amount by item (purchases minus returns)."
    />
  )
}
