'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Maintenance schedules"
      subtitle="Preventive maintenance due dates by asset."
      endpoint="/assets/maintenance-schedules"
      fields={[
        { key: 'asset_id', label: 'Asset', type: 'select', optionsKey: 'assets', required: true },
        { key: 'title', label: 'Task', required: true },
        { key: 'frequency_type', label: 'Frequency', type: 'select', optionsKey: 'frequencies', required: true },
        { key: 'frequency_value', label: 'Every', type: 'number', required: true },
        { key: 'next_due_date', label: 'Next due', type: 'date', required: true },
        { key: 'description', label: 'Notes', type: 'textarea' },
      ]}
      columns={[
        { key: 'asset_code', label: 'Asset' },
        { key: 'asset_name', label: 'Name' },
        { key: 'title', label: 'Task' },
        { key: 'frequency', label: 'Frequency' },
        { key: 'next_due_date', label: 'Next due' },
        { key: 'last_performed', label: 'Last done' },
        { key: 'is_active', label: 'Active' },
      ]}
    />
  )
}
