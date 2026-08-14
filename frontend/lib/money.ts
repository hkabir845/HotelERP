export const CURRENCY_CODE = 'BDT'

const MONEY_KEY =
  /(^|_)(amount|price|rate|total|balance|cost|paid|due|salary|wage|fee|rent|tax|fine|pay|debit|credit|value|revenue|budget|sales|opening|receipt|payment|net)s?$/i

export function isMoneyField(key: string) {
  const k = key.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()
  if (/occupancy|percent|pct|(^|_)(count|qty|quantity|nights|id)$/.test(k)) return false
  return MONEY_KEY.test(k) || /_(amount|price|rate|total|balance|cost|paid|due)$/.test(k)
}

export function formatMoney(
  value: number | string | null | undefined,
  options?: { digits?: number; empty?: string }
) {
  if (value === null || value === undefined || value === '') {
    return options?.empty ?? '—'
  }
  const n = Number(value)
  if (Number.isNaN(n)) return options?.empty ?? '—'
  const digits = options?.digits ?? 2
  const amount = n.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
  return `BDT ${amount}`
}

export function formatMoneyCell(key: string, value: unknown) {
  if (isMoneyField(key)) return formatMoney(value as number | string | null | undefined)
  if (value === null || value === undefined) return ''
  return String(value)
}

export function formatKeyedNumber(key: string, value: unknown) {
  if (typeof value !== 'number') return value == null || value === '' ? '—' : String(value)
  const normalized = String(key || '').replace(/[\s-]+/g, '_')
  if (isMoneyField(normalized)) return formatMoney(value)
  return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
}
