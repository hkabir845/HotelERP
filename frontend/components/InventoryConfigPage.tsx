'use client'
import ConfigMasterPage from '@/components/ConfigMasterPage'
import { INVENTORY_ENDPOINT, INVENTORY_MASTERS } from '@/lib/inventory-config'

export default function InventoryConfigPage({ kind }: { kind: string }) {
  return <ConfigMasterPage kind={kind} catalog={INVENTORY_MASTERS} endpoint={INVENTORY_ENDPOINT} />
}
