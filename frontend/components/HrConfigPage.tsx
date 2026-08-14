'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { HR_ENDPOINT, HR_MASTERS } from '@/lib/hr-config'

export default function HrConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={HR_MASTERS} endpoint={HR_ENDPOINT} />
}
