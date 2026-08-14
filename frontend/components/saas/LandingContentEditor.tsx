'use client'

type Props = {
  value: unknown
  onChange: (next: unknown) => void
  label?: string
}

function labelFromKey(key: string) {
  return key
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/^./, (s) => s.toUpperCase())
}

export default function LandingContentEditor({ value, onChange, label }: Props) {
  if (typeof value === 'string') {
    const long = value.length > 72 || value.includes('\n')
    return (
      <label className="block text-sm">
        {label && <span className="mb-1 block text-slate-600">{label}</span>}
        {long ? (
          <textarea
            className="min-h-[88px] w-full rounded-lg border px-3 py-2 font-sans text-sm"
            value={value}
            onChange={(e) => onChange(e.target.value)}
          />
        ) : (
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={value}
            onChange={(e) => onChange(e.target.value)}
          />
        )}
        <span className="mt-0.5 block text-right text-[10px] text-slate-400">{value.length} chars</span>
      </label>
    )
  }

  if (typeof value === 'boolean') {
    return (
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
        {label}
      </label>
    )
  }

  if (typeof value === 'number') {
    return (
      <label className="block text-sm">
        {label && <span className="mb-1 block text-slate-600">{label}</span>}
        <input
          type="number"
          className="w-full rounded-lg border px-3 py-2 text-sm"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
        />
      </label>
    )
  }

  if (Array.isArray(value)) {
    const isStringList = value.every((v) => typeof v === 'string')
    return (
      <div className="space-y-3 rounded-lg border border-slate-200 bg-slate-50/70 p-3">
        {label && <p className="text-sm font-medium text-slate-800">{label}</p>}
        {value.map((item, index) => (
          <div key={index} className="flex items-start gap-2">
            <div className="min-w-0 flex-1">
              <LandingContentEditor
                label={isStringList ? `${label || 'Item'} ${index + 1}` : undefined}
                value={item}
                onChange={(next) => {
                  const copy = [...value]
                  copy[index] = next
                  onChange(copy)
                }}
              />
            </div>
            <button
              type="button"
              className="mt-6 shrink-0 text-xs text-red-600 hover:underline"
              onClick={() => onChange(value.filter((_, i) => i !== index))}
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          className="text-xs font-medium text-indigo-600 hover:underline"
          onClick={() => {
            if (isStringList) onChange([...value, ''])
            else if (value[0] && typeof value[0] === 'object') {
              onChange([...value, JSON.parse(JSON.stringify(value[0]))])
            } else onChange([...value, ''])
          }}
        >
          + Add {label || 'item'}
        </button>
      </div>
    )
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
    return (
      <div className="space-y-4">
        {label && <h4 className="text-sm font-semibold text-slate-900">{label}</h4>}
        <div className="grid gap-3 sm:grid-cols-2">
          {entries.map(([key, child]) => {
            const nested = child && typeof child === 'object'
            return (
              <div key={key} className={nested ? 'sm:col-span-2' : ''}>
                <LandingContentEditor
                  label={labelFromKey(key)}
                  value={child}
                  onChange={(next) => onChange({ ...(value as object), [key]: next })}
                />
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  return null
}
