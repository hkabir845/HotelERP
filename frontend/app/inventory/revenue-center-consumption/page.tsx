'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Revenue Center Consumption"
      subtitle="Stock issued to restaurant, room service, or other outlets."
      endpoint="/inventory/consumptions"
      query="?kind=revenue_center"
      createPath="/inventory/revenue-center-consumption/new"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'consumption_date', label: 'Date' },
        { key: 'revenue_center', label: 'Revenue center' },
        { key: 'warehouse_name', label: 'Warehouse' },
        { key: 'total_cost', label: 'Cost' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
