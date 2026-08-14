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
      title="Tomorrow's Departures"
      subtitle="Guests scheduled to depart tomorrow"
      query={{ check_out_date: shiftDate(1) }}
      emptyText="No departures tomorrow."
    />
  )
}
