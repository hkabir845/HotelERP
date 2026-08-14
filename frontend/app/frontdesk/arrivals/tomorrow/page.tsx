'use client'
import ReservationFilterPage from '@/components/ReservationFilterPage'

function shiftDate(days: number) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().split('T')[0]
}

export default function Page() {
  return (
    <ReservationFilterPage
      title="Tomorrow's Arrivals"
      subtitle="Guests scheduled to arrive tomorrow"
      query={{ check_in_date: shiftDate(1) }}
      emptyText="No arrivals tomorrow."
    />
  )
}
