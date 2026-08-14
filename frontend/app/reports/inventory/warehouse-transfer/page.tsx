'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/inventory/reports"
      kind="warehouse-transfer"
      title="Warehouse Transfer Report"
      subtitle="Posted transfers by item between warehouses."
    />
  )
}
