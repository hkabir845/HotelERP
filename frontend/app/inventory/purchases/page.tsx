'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Purchase / Return List"
      subtitle="Posted purchases add stock; returns deduct stock and credit the supplier."
      endpoint="/inventory/purchases"
      createPath="/inventory/purchases/new"
      createLabel="Purchase"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'purchase_date', label: 'Date' },
        { key: 'supplier_name', label: 'Supplier' },
        { key: 'warehouse_name', label: 'Warehouse' },
        { key: 'is_return', label: 'Return' },
        { key: 'total_amount', label: 'Amount' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
