/**
 * Built-in hotel COA codes — mirrors backend api.services.hotel_coa.HotelCoaCode
 */

export type CoaPick = {
  id: number
  account_code: string
  account_name?: string
  code?: string
  name?: string
  book?: string
  is_group?: boolean
  account_type?: string
}

export const COA = {
  CASH: '1110',
  PETTY_CASH: '1115',
  BANK: '1120',
  BANK_CARD: '1125',
  AR: '1130',
  AR_CORPORATE: '1135',
  AP: '2100',
  AP_FOOD: '2110',
  GUEST_DEPOSITS: '2120',
  VAT: '2130',
  ROOM_REV: '4100',
  FNB_REV: '4200',
  BANQUET_REV: '4210',
  OTHER_INCOME: '4300',
  PURCHASES: '5300',
  RENT: '6200',
  GENERAL_OPEX: '6920',
  SALARIES: '5100',
  LOAN_RECV: '1160',
  LOAN_PAY: '2410',
  INTEREST_INCOME: '4410',
  INTEREST_EXPENSE: '6620',
} as const

export const COA_SETTLEMENT_PREFERENCE = [COA.BANK, COA.CASH] as const

export function coaSuffix(code: string) {
  /** Prefer plain FSERP-style codes; still accept legacy "1-1110". */
  const c = String(code || '').trim()
  if (!c.includes('-')) return c
  const [left, ...rest] = c.split('-')
  if (/^\d+$/.test(left) && rest.length) return rest.join('-')
  return c
}

export function normalizeCoaPick(row: any): CoaPick {
  return {
    id: Number(row.id),
    account_code: String(row.account_code || row.code || ''),
    account_name: String(row.account_name || row.name || ''),
    code: String(row.account_code || row.code || ''),
    name: String(row.account_name || row.name || ''),
    book: row.book || '',
    is_group: !!row.is_group,
    account_type: row.account_type || '',
  }
}

export function coaIdForCode(code: string, options: CoaPick[]): string {
  const want = coaSuffix(code)
  if (!want) return ''
  const match = options.find((a) => coaSuffix(a.account_code || a.code || '') === want)
  return match && match.id > 0 ? String(match.id) : ''
}

export function coaIdForFirstCode(codes: readonly string[], options: CoaPick[]): string {
  for (const code of codes) {
    const id = coaIdForCode(code, options)
    if (id) return id
  }
  return ''
}

export function recommendedCoaLabel(code: string, options: CoaPick[]): string {
  const want = coaSuffix(code)
  const match = options.find((a) => coaSuffix(a.account_code || a.code || '') === want)
  if (match) {
    const name = match.account_name || match.name || ''
    const c = match.account_code || match.code || code
    return name ? `${coaSuffix(c)} — ${name}` : String(c)
  }
  return code
}

export function templateCoaOptionLabel(code: string, options: CoaPick[]): string {
  return `— Recommended: ${recommendedCoaLabel(code, options)} —`
}

export function suggestedSettlementAccountId(options: CoaPick[]): string {
  return coaIdForFirstCode(COA_SETTLEMENT_PREFERENCE, options)
}

export function suggestedExpenseAccountId(options: CoaPick[], purpose: 'purchases' | 'rent' | 'general' | 'salaries' = 'general'): string {
  const map = {
    purchases: COA.PURCHASES,
    rent: COA.RENT,
    general: COA.GENERAL_OPEX,
    salaries: COA.SALARIES,
  } as const
  return coaIdForCode(map[purpose], options) || coaIdForCode(COA.GENERAL_OPEX, options)
}

export function suggestedIncomeAccountId(options: CoaPick[], purpose: 'room' | 'fnb' | 'banquet' | 'other' = 'room'): string {
  const map = {
    room: COA.ROOM_REV,
    fnb: COA.FNB_REV,
    banquet: COA.BANQUET_REV,
    other: COA.OTHER_INCOME,
  } as const
  return coaIdForCode(map[purpose], options) || coaIdForCode(COA.ROOM_REV, options)
}

export function suggestedLoanAccountIds(options: CoaPick[], direction: 'borrowed' | 'lent' = 'borrowed') {
  if (direction === 'lent') {
    return {
      principal_account_id: coaIdForCode(COA.LOAN_RECV, options),
      settlement_account_id: suggestedSettlementAccountId(options),
      interest_account_id: coaIdForCode(COA.INTEREST_INCOME, options),
    }
  }
  return {
    principal_account_id: coaIdForCode(COA.LOAN_PAY, options),
    settlement_account_id: suggestedSettlementAccountId(options),
    interest_account_id: coaIdForCode(COA.INTEREST_EXPENSE, options),
  }
}

export function leafAccounts(rows: any[]): CoaPick[] {
  return (rows || [])
    .map(normalizeCoaPick)
    .filter((a) => a.id > 0 && !a.is_group)
}
