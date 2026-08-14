'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="Leads"
      subtitle="New → contacted → qualified → convert to customer, or mark lost."
      endpoint="/crm/leads"
      fields={[
        { key: 'name', label: 'Lead / guest', required: true },
        { key: 'source_id', label: 'Source', type: 'select', optionsKey: 'lead_sources' },
        { key: 'company', label: 'Company' },
        { key: 'phone', label: 'Phone' },
        { key: 'email', label: 'Email', type: 'email' },
        { key: 'expected_value', label: 'Expected value', type: 'number' },
        { key: 'next_followup', label: 'Next follow-up', type: 'date' },
        { key: 'notes', label: 'Requirement', type: 'textarea' },
      ]}
      columns={[
        { key: 'number', label: 'No.' },
        { key: 'name', label: 'Lead' },
        { key: 'company', label: 'Company' },
        { key: 'source_name', label: 'Source' },
        { key: 'phone', label: 'Phone' },
        { key: 'expected_value', label: 'Value' },
        { key: 'next_followup', label: 'Follow-up' },
        { key: 'status', label: 'Status' },
      ]}
      actions={[
        { id: 'contact', label: 'Contacted', flag: 'can_contact' },
        { id: 'qualify', label: 'Qualify', flag: 'can_qualify' },
        { id: 'convert', label: 'Convert', flag: 'can_convert', tone: 'emerald' },
        { id: 'lose', label: 'Lost', flag: 'can_lose', tone: 'red' },
      ]}
    />
  )
}
