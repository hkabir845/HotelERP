'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { UTIL_MASTERS } from '@/lib/remaining-config'

export default function UtilConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={UTIL_MASTERS} endpoint="/utilities/config" />
}
