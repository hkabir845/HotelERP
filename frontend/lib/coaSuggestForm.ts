/**
 * Touch-aware GL account auto-suggest helpers (FSERP coaSuggestForm pattern).
 */

import type { CoaPick } from '@/lib/coaDefaults'
import { coaIdForCode } from '@/lib/coaDefaults'

export function mergeSuggestedStringField(current: string, suggested: string, touched: boolean): string {
  if (touched) return current
  if (String(current || '').trim() !== '') return current
  return suggested || ''
}

export function syncFieldTouched(touched: Set<string>, fieldKey: string, value: string) {
  if (String(value || '').trim() !== '') touched.add(fieldKey)
  else touched.delete(fieldKey)
}

export function parseSuggestedCoaId(suggested: string | number | null | undefined): number | undefined {
  if (suggested == null || suggested === '') return undefined
  const n = typeof suggested === 'number' ? suggested : parseInt(String(suggested), 10)
  return Number.isFinite(n) && n > 0 ? n : undefined
}

export function coaPickFromRows(rows: { id: number; account_code?: string; code?: string; account_name?: string; name?: string }[]): CoaPick[] {
  return rows.map((a) => ({
    id: a.id,
    account_code: String(a.account_code || a.code || ''),
    account_name: a.account_name != null ? String(a.account_name) : a.name != null ? String(a.name) : undefined,
  }))
}

export { coaIdForCode }
