'use client'
import RecordWorkbench from '@/components/RecordWorkbench'

type Field = {
  key: string
  label: string
  type?: 'text' | 'number' | 'date' | 'datetime-local' | 'email' | 'textarea' | 'select' | 'checkbox'
  optionsKey?: string
  required?: boolean
}

export default function ServiceDeskPage({
  title,
  subtitle,
  kind,
  fields,
  columns,
}: {
  title: string
  subtitle: string
  kind: string
  fields: Field[]
  columns: { key: string; label: string }[]
}) {
  return (
    <RecordWorkbench
      title={title}
      subtitle={subtitle}
      endpoint="/services"
      query={`?kind=${kind}`}
      extraBody={{ kind }}
      fields={fields}
      columns={columns}
      actions={[
        { id: 'complete', label: 'Complete', flag: 'can_complete', tone: 'emerald' },
        { id: 'cancel', label: 'Cancel', flag: 'can_cancel', tone: 'red' },
      ]}
    />
  )
}
