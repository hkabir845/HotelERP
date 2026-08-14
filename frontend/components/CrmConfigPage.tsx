'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { CRM_ENDPOINT, CRM_MASTERS } from '@/lib/crm-config'

export default function CrmConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={CRM_MASTERS} endpoint={CRM_ENDPOINT} />
}
