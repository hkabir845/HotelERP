'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

type DrillStep = {
  step: string
  label: string
  description?: string | null
  path?: string | null
  related_id?: number | null
}

export default function VoucherDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id
  const [row, setRow] = useState<any>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => {
    apiClient
      .get(`/accounts/vouchers/${id}`)
      .then((res) => setRow(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }

  useEffect(() => {
    if (id) load()
  }, [id])

  const post = async () => {
    setBusy(true)
    setError('')
    try {
      const res = await apiClient.post(`/accounts/vouchers/${id}`, { action: 'post' })
      setRow(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Post failed')
    } finally {
      setBusy(false)
    }
  }

  const chain: DrillStep[] = row?.drill_chain?.length
    ? row.drill_chain
    : row?.source_label
      ? [
          {
            step: 'journal',
            label: 'Journal voucher',
            description: row.description,
            path: `/accounts/vouchers/${row.id}`,
            related_id: row.id,
          },
          {
            step: row.related_type || 'source',
            label: row.source_label,
            description: row.source_description,
            path: row.source_path,
            related_id: row.related_id,
          },
        ]
      : []

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <button type="button" onClick={() => router.push('/accounts/vouchers')} className="text-sm text-indigo-700">
            Back to list
          </button>
          {error && <p className="mt-3 text-red-600">{error}</p>}
          {!row ? (
            <p className="mt-6 text-slate-500">Loading…</p>
          ) : (
            <>
              <div className="mt-4 flex items-start justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{row.voucher_number}</h1>
                  <p className="mt-1 text-gray-600">
                    {row.voucher_type?.replace('_', ' ')} · {row.date} · {row.status}
                  </p>
                  {row.description && <p className="mt-2 text-gray-700">{row.description}</p>}
                </div>
                {row.status !== 'posted' && (
                  <button type="button" disabled={busy} onClick={post} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
                    Post
                  </button>
                )}
              </div>

              {chain.length > 0 && (
                <div className="mt-6 rounded-xl border bg-white p-4">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Dig-down trail</h2>
                  <ol className="mt-3 space-y-3">
                    {chain.map((step, i) => (
                      <li key={`${step.step}-${i}`} className="flex gap-3">
                        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-800">
                          {i + 1}
                        </span>
                        <div>
                          <div className="font-medium text-gray-900">
                            {step.path ? (
                              <Link href={step.path} className="text-indigo-700 hover:underline">
                                {step.label}
                                {step.related_id && step.step !== 'journal' ? ` #${step.related_id}` : ''}
                              </Link>
                            ) : (
                              <>
                                {step.label}
                                {step.related_id ? ` #${step.related_id}` : ''}
                              </>
                            )}
                          </div>
                          {step.description && <p className="mt-0.5 text-sm text-slate-600">{step.description}</p>}
                        </div>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              <div className="mt-6 overflow-hidden rounded-xl border bg-white">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-50 text-left text-slate-600">
                    <tr>
                      <th className="px-4 py-3">Account</th>
                      <th className="px-4 py-3">Narration</th>
                      <th className="px-4 py-3">Source</th>
                      <th className="px-4 py-3 text-right">Debit</th>
                      <th className="px-4 py-3 text-right">Credit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(row.lines || []).map((line: any) => (
                      <tr key={line.id} className="border-t">
                        <td className="px-4 py-3">
                          {line.account_code} {line.account_name}
                        </td>
                        <td className="px-4 py-3">{line.description || '—'}</td>
                        <td className="px-4 py-3">
                          {line.source_label ? (
                            <div>
                              {line.source_path ? (
                                <Link href={line.source_path} className="text-indigo-700 hover:underline">
                                  {line.source_label}
                                </Link>
                              ) : (
                                <span>{line.source_label}</span>
                              )}
                              {line.source_description && (
                                <div className="mt-0.5 text-xs text-slate-500">{line.source_description}</div>
                              )}
                            </div>
                          ) : (
                            '—'
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">{line.debit ? formatMoney(line.debit) : ''}</td>
                        <td className="px-4 py-3 text-right">{line.credit ? formatMoney(line.credit) : ''}</td>
                      </tr>
                    ))}
                    <tr className="border-t font-semibold">
                      <td className="px-4 py-3" colSpan={3}>
                        Total
                      </td>
                      <td className="px-4 py-3 text-right">{formatMoney(row.total_debit || 0)}</td>
                      <td className="px-4 py-3 text-right">{formatMoney(row.total_credit || 0)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
