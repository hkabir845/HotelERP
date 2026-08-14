'use client'

import { Suspense, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatKeyedNumber } from '@/lib/money'

function monthStart() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

const TXN_KINDS = new Set([
  'cash-book',
  'bank-book',
  'general-ledger',
  'group-ledger',
  'transaction-detail',
  'daily-cash-sheet',
])

const AMOUNT_HEADERS = new Set([
  'Debit',
  'Credit',
  'Balance',
  'Amount',
  'Opening',
  'Opening balance',
  'Net expense',
  'Receipt',
  'Payment',
])

export default function AccountReportPage(props: {
  kind: string
  title: string
  subtitle: string
  needsAccount?: boolean
}) {
  return (
    <Suspense
      fallback={
        <ProtectedRoute>
          <div className="flex h-screen bg-gray-200">
            <Sidebar />
            <main className="ml-64 flex-1 p-6 text-slate-500">Loading report…</main>
          </div>
        </ProtectedRoute>
      }
    >
      <AccountReportInner {...props} />
    </Suspense>
  )
}

function AccountReportInner({
  kind,
  title,
  subtitle,
  needsAccount,
}: {
  kind: string
  title: string
  subtitle: string
  needsAccount?: boolean
}) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [from, setFrom] = useState(searchParams.get('from') || monthStart())
  const [to, setTo] = useState(searchParams.get('to') || today())
  const [accountId, setAccountId] = useState(searchParams.get('account_id') || '')
  const [accounts, setAccounts] = useState<{ id: number; name: string; is_group: boolean }[]>([])
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<any[]>([])
  const [summary, setSummary] = useState<Record<string, any>>({})
  const [diggable, setDiggable] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = (override?: { from?: string; to?: string; accountId?: string }) => {
    const f = override?.from ?? from
    const t = override?.to ?? to
    const aid = override?.accountId ?? accountId
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ from: f, to: t })
    if (aid) params.set('account_id', aid)
    apiClient
      .get(`/accounts/reports/${kind}?${params.toString()}`)
      .then((res) => {
        setColumns(res.data.columns || [])
        setRows(res.data.rows || [])
        setSummary(res.data.summary || {})
        setDiggable(Boolean(res.data.diggable))
        if (res.data.accounts) setAccounts(res.data.accounts)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const qFrom = searchParams.get('from')
    const qTo = searchParams.get('to')
    const qAccount = searchParams.get('account_id')
    const nextFrom = qFrom || from
    const nextTo = qTo || to
    const nextAccount = qAccount != null ? qAccount : accountId
    if (qFrom) setFrom(qFrom)
    if (qTo) setTo(qTo)
    if (qAccount != null) setAccountId(qAccount)
    load({ from: nextFrom, to: nextTo, accountId: nextAccount })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kind, searchParams])

  const drillToLedger = (rowAccountId: number | null | undefined) => {
    if (!rowAccountId) return
    const params = new URLSearchParams({ from, to, account_id: String(rowAccountId) })
    router.push(`/reports/accounts/general-ledger?${params.toString()}`)
  }

  const drillToVoucher = (journalId: number | null | undefined) => {
    if (!journalId) return
    router.push(`/accounts/vouchers/${journalId}`)
  }

  const isTxnRow = (row: any) => Boolean(row?.date && (row?.voucher != null || row?.journal_entry_id))

  const displayColumns =
    TXN_KINDS.has(kind) && columns.includes('Source') && !columns.includes('Description')
      ? [...columns.slice(0, columns.indexOf('Source') + 1), 'Description']
      : columns

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-1 text-gray-600">{subtitle}</p>
          <p className="mt-2 text-sm text-slate-500">
            Dig step-by-step: amount → ledger lines → voucher → root source (with description at each step).
          </p>

          <div className="mt-6 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">From</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={from} onChange={(e) => setFrom(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">To</span>
              <input type="date" className="rounded-lg border px-3 py-2" value={to} onChange={(e) => setTo(e.target.value)} />
            </label>
            {needsAccount && (
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Account / group</span>
                <select className="min-w-[220px] rounded-lg border px-3 py-2" value={accountId} onChange={(e) => setAccountId(e.target.value)}>
                  <option value="">All accounts</option>
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                      {a.is_group ? ' (group)' : ''}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <button type="button" onClick={() => load()} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
              Run
            </button>
          </div>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          {summary && Object.keys(summary).length > 0 && (
            <div className="mt-4 flex flex-wrap gap-4 text-sm">
              {Object.entries(summary).map(([key, value]) => (
                <div key={key} className="rounded-lg border bg-white px-4 py-2">
                  <div className="capitalize text-slate-500">{key.replace(/_/g, ' ')}</div>
                  <div className="font-semibold">{typeof value === 'number' ? formatKeyedNumber(key, value) : String(value)}</div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : rows.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No posted transactions in this period.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    {displayColumns.map((h) => (
                      <th key={h} className="whitespace-nowrap px-3 py-2 font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => {
                    const cells = mapRow(row, kind, displayColumns)
                    const clickableSummary = diggable && row.account_id && !isTxnRow(row)
                    const txn = isTxnRow(row)
                    return (
                      <tr
                        key={row.id || `${row.account_id || 'r'}-${idx}`}
                        className={`border-t ${clickableSummary ? 'cursor-pointer hover:bg-indigo-50/60' : ''}`}
                        onClick={clickableSummary ? () => drillToLedger(row.account_id) : undefined}
                        title={clickableSummary ? 'Step 1: open general ledger for this account' : undefined}
                      >
                        {cells.map((cell, i) => {
                          const header = displayColumns[i]
                          const isAmount = typeof cell === 'number' && AMOUNT_HEADERS.has(header)
                          return (
                            <td
                              key={i}
                              className={`px-3 py-2 ${typeof cell === 'number' ? 'text-right tabular-nums' : ''} ${
                                (clickableSummary && isAmount) || (txn && isAmount && row.journal_entry_id)
                                  ? 'font-medium text-indigo-700'
                                  : ''
                              }`}
                            >
                              {renderCell(cell, header, row, {
                                onAmountClick: () => {
                                  if (txn && row.journal_entry_id) drillToVoucher(row.journal_entry_id)
                                  else if (clickableSummary) drillToLedger(row.account_id)
                                },
                                clickableAmount: (txn && row.journal_entry_id) || clickableSummary,
                              })}
                            </td>
                          )
                        })}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

function renderCell(
  cell: any,
  header: string | undefined,
  row: any,
  opts: { onAmountClick?: () => void; clickableAmount?: boolean } = {},
) {
  if ((header === 'Voucher' || header === 'Journal') && row.journal_entry_id) {
    return (
      <Link
        href={`/accounts/vouchers/${row.journal_entry_id}`}
        className="text-indigo-700 hover:underline"
        onClick={(e) => e.stopPropagation()}
        title="Step 2: open journal voucher"
      >
        {row.voucher || cell || '—'}
      </Link>
    )
  }
  if (header === 'Source') {
    if (row.source_label) {
      const inner = (
        <span className="text-indigo-700 hover:underline" title={row.source_description || row.source_label}>
          {row.source_label}
        </span>
      )
      if (row.source_path) {
        return (
          <Link href={row.source_path} onClick={(e) => e.stopPropagation()} title={row.source_description || 'Step 3: root source'}>
            {inner}
          </Link>
        )
      }
      return inner
    }
    return '—'
  }
  if (header === 'Description') {
    return <span className="text-slate-600">{row.source_description || row.narration || '—'}</span>
  }
  if (typeof cell === 'number') {
    const keyHint =
      header?.toLowerCase().includes('debit') || header === 'Receipt'
        ? 'debit'
        : header?.toLowerCase().includes('credit') || header === 'Payment'
          ? 'credit'
          : 'balance'
    const formatted = formatKeyedNumber(keyHint, cell)
    if (opts.clickableAmount && opts.onAmountClick) {
      return (
        <button
          type="button"
          className="text-indigo-700 underline-offset-2 hover:underline"
          title={row.journal_entry_id ? 'Step 2: open voucher' : 'Step 1: open ledger'}
          onClick={(e) => {
            e.stopPropagation()
            opts.onAmountClick?.()
          }}
        >
          {formatted}
        </button>
      )
    }
    return formatted
  }
  if (cell == null || cell === '') return '—'
  return String(cell)
}

function mapRow(row: any, kind: string, columns: string[]): any[] {
  if (kind === 'daily-cash-sheet') {
    const base = [row.date, row.voucher, row.narration, row.receipt, row.payment, row.source_label]
    return columns.includes('Description') ? [...base, row.source_description] : base
  }
  if (row.date && (row.voucher != null || row.journal_entry_id)) {
    const base = [row.date, row.voucher, row.account, row.narration, row.debit, row.credit, row.balance, row.source_label]
    return columns.includes('Description') ? [...base, row.source_description] : base
  }
  if (kind === 'opening-balance') return [row.code, row.account, row.account_type, row.opening, row.as_of, row.voucher]
  if (kind === 'account-balance') return [row.code, row.account, row.account_type, row.balance]
  if (kind === 'expense') return [row.code, row.account, row.debit, row.credit, row.net]
  if (kind === 'trial-balance') return [row.code, row.account, row.debit, row.credit]
  if (kind === 'profit-loss') return [row.account, row.amount]
  if (kind === 'balance-sheet') return [row.account, row.account_type, row.amount]
  if ((kind === 'general-ledger' || kind === 'group-ledger') && !row.date) {
    return [row.account, row.account_type, row.opening, row.debit, row.credit, row.balance]
  }
  return Object.values(row).filter((v) => typeof v !== 'object')
}
