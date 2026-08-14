'use client'
import ForecastGridPage from '@/components/ForecastGridPage'

export default function Page() {
  return (
    <ForecastGridPage
      title="Room Rate Schedule"
      subtitle="Daily rates by room type. Special rates override the base rate for matching dates."
      endpoint="/frontdesk/rate-schedule"
      mode="rate"
    />
  )
}
