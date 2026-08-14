'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Requisition List"
      subtitle="Department requests. Approve, then fulfill to issue warehouse stock."
      endpoint="/inventory/requisitions"
      createPath="/inventory/requisitions/new"
      postAction="fulfill"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'requested_date', label: 'Date' },
        { key: 'department', label: 'Department' },
        { key: 'warehouse_name', label: 'Warehouse' },
        { key: 'status', label: 'Status' },
        { key: 'requested_by', label: 'Requested by' },
      ]}
    />
  )
}
