'use client'
import ReservationFilterPage from '@/components/ReservationFilterPage'

function weekRange() {
  const today = new Date()
  const start = new Date(today)
  start.setDate(today.getDate() - today.getDay())
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return {
    from: start.toISOString().split('T')[0],
    to: end.toISOString().split('T')[0],
  }
}

export default function Page() {
  const { from, to } = weekRange()
  return (
    <ReservationFilterPage
      title="This Week's Arrivals"
      subtitle={`Guests arriving ${from} to ${to}`}
      query={{ check_in_date_from: from, check_in_date_to: to }}
      emptyText="No arrivals this week."
    />
  )
}
