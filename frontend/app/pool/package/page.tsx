'use client'
import ServiceDeskPage from '@/components/ServiceDeskPage'
export default function Page() {
  return (
    <ServiceDeskPage
      title="Pool package"
      subtitle="Sellable pool packages (day pass, family, seasonal)."
      kind="pool_package"
      fields={[
        { key: 'item', label: 'Package name', required: true },
        { key: 'amount', label: 'Price', type: 'number', required: true },
        { key: 'notes', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'reference', label: 'Ref' },
        { key: 'item', label: 'Package' },
        { key: 'amount', label: 'Price' },
        { key: 'notes', label: 'Notes' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
