'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { BANQUET_ENDPOINT, BANQUET_MASTERS } from '@/lib/banquet-config'

export default function BanquetConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={BANQUET_MASTERS} endpoint={BANQUET_ENDPOINT} />
}
