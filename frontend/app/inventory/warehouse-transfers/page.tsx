'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Warehouse Transfer List"
      subtitle="Posted transfers move quantity between warehouses."
      endpoint="/inventory/transfers"
      createPath="/inventory/warehouse-transfers/new"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'transfer_date', label: 'Date' },
        { key: 'from_warehouse_name', label: 'From' },
        { key: 'to_warehouse_name', label: 'To' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
