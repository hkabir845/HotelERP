'use client'
import BanquetEventList from '@/components/BanquetEventList'
export default function Page() {
  return (
    <BanquetEventList
      title="Pending Event Folios"
      subtitle="Events with an outstanding balance. Collect cash, card, bank, or mobile against the folio."
      pending
    />
  )
}
