'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Laundry stock"
      subtitle="Wash chemicals, bags, and linen stock for laundry POS."
      kind="laundry_stock"
      fields={[
        { key: 'item', label: 'Item', required: true },
        { key: 'quantity', label: 'Qty', type: 'number', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'item', label: 'Item' },
        { key: 'quantity', label: 'Qty' },
        { key: 'notes', label: 'Notes' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
