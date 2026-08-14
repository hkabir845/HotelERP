'use client'
import ForecastGridPage from '@/components/ForecastGridPage'

export default function Page() {
  return (
    <ForecastGridPage
      title="Room Availability Forecast"
      subtitle="Night-by-night status for each room. A = available, O = occupied, B = blocked."
      endpoint="/frontdesk/forecast/availability"
      mode="room"
    />
  )
}
