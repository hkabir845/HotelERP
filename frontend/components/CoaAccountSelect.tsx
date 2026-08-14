'use client'

import { templateCoaOptionLabel, type CoaPick, coaSuffix } from '@/lib/coaDefaults'

type Props = {
  value: string
  onChange: (value: string) => void
  accounts: CoaPick[]
  /** Stable template code shown as “Recommended” empty option */
  recommendedCode?: string
  /** When set, prefer this account id as the empty-option recommendation label */
  recommendedId?: string | number
  label?: string
  hint?: string
  allowEmpty?: boolean
  filter?: (a: CoaPick) => boolean
  className?: string
  disabled?: boolean
}

/** Editable account picker with recommended prefill label (FSERP-style). */
export default function CoaAccountSelect({
  value,
  onChange,
  accounts,
  recommendedCode,
  recommendedId,
  label,
  hint,
  allowEmpty = true,
  filter,
  className = '',
  disabled,
}: Props) {
  const list = (filter ? accounts.filter(filter) : accounts).filter((a) => !a.is_group)
  const recId = recommendedId != null && Number(recommendedId) > 0 ? String(recommendedId) : ''
  const recCode = recommendedCode || ''
  const emptyLabel = recCode
    ? templateCoaOptionLabel(recCode, list)
    : recId
      ? `— Recommended: ${list.find((a) => String(a.id) === recId)?.account_name || list.find((a) => String(a.id) === recId)?.name || recId} —`
      : '— Select account —'

  return (
    <label className={`block text-sm ${className}`}>
      {label ? <span className="mb-1 block font-medium text-gray-700">{label}</span> : null}
      <select
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
      >
        {allowEmpty ? <option value="">{emptyLabel}</option> : null}
        {list.map((a) => {
          const code = coaSuffix(a.account_code || a.code || '')
          const name = a.account_name || a.name || ''
          return (
            <option key={a.id} value={String(a.id)}>
              {code} — {name}
            </option>
          )
        })}
      </select>
      {hint ? <span className="mt-1 block text-xs text-gray-500">{hint}</span> : null}
    </label>
  )
}
