'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/assets"
      kind="depreciation"
      title="Asset Depreciation"
      subtitle="Book value from purchase cost, rate, and accumulated depreciation."
      hideDates
    />
  )
}
