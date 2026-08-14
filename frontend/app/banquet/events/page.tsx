'use client'
import BanquetEventList from '@/components/BanquetEventList'
export default function Page() {
  return (
    <BanquetEventList
      title="Event List"
      subtitle="Enquiry → confirm → start → collect → complete. Same venue and session cannot double-book."
      createPath="/banquet/events/new"
    />
  )
}
