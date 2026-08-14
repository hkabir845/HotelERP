'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Supplier Payments"
      subtitle="Payments against posted purchases. Due is purchase − return − paid."
      endpoint="/inventory/payments"
      createPath="/inventory/suppliers/payments/new"
      createLabel="Pay"
      columns={[
        { key: 'payment_date', label: 'Date' },
        { key: 'supplier_name', label: 'Supplier' },
        { key: 'method', label: 'Method' },
        { key: 'reference', label: 'Reference' },
        { key: 'amount', label: 'Amount' },
        { key: 'created_by', label: 'By' },
      ]}
    />
  )
}
