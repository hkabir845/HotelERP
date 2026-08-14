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
      title="Yesterday's Departures"
      subtitle="Guests scheduled to depart yesterday"
      query={{ check_out_date: shiftDate(-1) }}
      emptyText="No departures yesterday."
    />
  )
}
