'use client'
import ForecastGridPage from '@/components/ForecastGridPage'

export default function Page() {
  return (
    <ForecastGridPage
      title="Room Type Availability Forecast"
      subtitle="Available / total rooms by type for each night, from live reservations and blocks."
      endpoint="/frontdesk/forecast/room-type"
      mode="room-type"
    />
  )
}
