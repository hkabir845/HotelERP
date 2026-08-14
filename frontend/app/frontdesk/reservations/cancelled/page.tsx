'use client'
import ReservationFilterPage from '@/components/ReservationFilterPage'

export default function Page() {
  return (
    <ReservationFilterPage
      title="Cancelled / Void / No-Show"
      subtitle="Reservations that were cancelled or marked no-show"
      query={{ status: 'cancelled,no_show' }}
      emptyText="No cancelled or no-show reservations."
    />
  )
}
