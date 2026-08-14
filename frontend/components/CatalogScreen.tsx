'use client'

import ServiceRecordsPage from '@/components/ServiceRecordsPage'
import ActionScreen from '@/components/ActionScreen'
import { getOpsPreset } from '@/lib/ops-presets'

export default function CatalogScreen({
  title,
  subtitle,
  kind,
  endpoint = '/catalog',
  readOnly = false,
}: {
  title: string
  subtitle?: string
  kind: string
  endpoint?: string
  readOnly?: boolean
}) {
  const preset = getOpsPreset(kind)
  if (preset && !readOnly) {
    return <ActionScreen title={title} kind={kind} subtitle={subtitle} />
  }
  return (
    <ServiceRecordsPage
      title={title}
      subtitle={subtitle || 'Add and review records for this screen.'}
      endpoint={endpoint}
      extraParams={{ kind }}
      createKind={kind}
      readOnly={readOnly}
      fields={[
        { key: 'name', label: 'Name' },
        { key: 'code', label: 'Code' },
        { key: 'amount', label: 'Amount (BDT)', type: 'number' },
        { key: 'notes', label: 'Notes' },
      ]}
      columns={[
        { key: 'name', label: 'Name' },
        { key: 'code', label: 'Code' },
        { key: 'amount', label: 'Amount (BDT)' },
        { key: 'status', label: 'Status' },
        { key: 'notes', label: 'Notes' },
      ]}
    />
  )
}
