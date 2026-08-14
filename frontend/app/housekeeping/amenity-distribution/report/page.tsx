'use client'
import FnbReportPage from '@/components/FnbReportPage'
export default function Page() {
  return (
    <FnbReportPage
      endpoint="/housekeeping/amenity-distribution"
      kind="report"
      title="Amenity Distribution Report"
      subtitle="Amenities issued to rooms in the period, grouped by item."
    />
  )
}
