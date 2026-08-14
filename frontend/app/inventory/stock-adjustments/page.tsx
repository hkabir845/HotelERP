'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Stock Adjustment List"
      subtitle="Add increases stock; remove writes it off. Post to update the warehouse."
      endpoint="/inventory/adjustments"
      createPath="/inventory/stock-adjustments/add"
      createLabel="Add"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'adjustment_date', label: 'Date' },
        { key: 'adjustment_type', label: 'Type' },
        { key: 'warehouse_name', label: 'Warehouse' },
        { key: 'reason', label: 'Reason' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
