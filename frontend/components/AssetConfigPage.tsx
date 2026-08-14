'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { ASSET_MASTERS } from '@/lib/remaining-config'

export default function AssetConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={ASSET_MASTERS} endpoint="/assets/config" />
}
