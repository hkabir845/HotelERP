'use client'
import InventoryDocList from '@/components/InventoryDocList'
export default function Page() {
  return (
    <InventoryDocList
      title="Amenities Consumption"
      subtitle="Amenities issued from store to rooms or housekeeping."
      endpoint="/inventory/consumptions"
      query="?kind=amenities"
      createPath="/inventory/amenities-consumption/new"
      columns={[
        { key: 'number', label: 'Number' },
        { key: 'consumption_date', label: 'Date' },
        { key: 'revenue_center', label: 'Amenity / area' },
        { key: 'warehouse_name', label: 'Warehouse' },
        { key: 'total_cost', label: 'Cost' },
        { key: 'status', label: 'Status' },
      ]}
    />
  )
}
