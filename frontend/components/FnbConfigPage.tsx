'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { FNB_ENDPOINT, FNB_MASTERS } from '@/lib/fnb-config'

export default function FnbConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={FNB_MASTERS} endpoint={FNB_ENDPOINT} />
}
