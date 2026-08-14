'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Next Follow-Up Tasks"
      subtitle="Open follow-up tasks and other open CRM tasks."
      endpoint="/crm/tasks"
      query="?followup=1"
      fields={[
        { key: 'title', label: 'Task', required: true },
        { key: 'contact_name', label: 'Guest / lead' },
        { key: 'phone', label: 'Phone' },
        { key: 'due_at', label: 'Due', type: 'datetime-local' },
        { key: 'is_followup', label: 'Follow-up task', type: 'checkbox' },
        { key: 'notes', label: 'Details', type: 'textarea' },
      ]}
      columns={[
        { key: 'title', label: 'Task' },
        { key: 'contact_name', label: 'Contact' },
        { key: 'due_at', label: 'Due' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'start', label: 'Start', flag: 'can_start' },
        { id: 'complete', label: 'Done', flag: 'can_complete', tone: 'emerald' },
        { id: 'cancel', label: 'Cancel', flag: 'can_cancel', tone: 'red' },
      ]}
    />
  )
}
