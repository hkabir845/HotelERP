'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { Plus, Trash2 } from 'lucide-react'
import {
  COA,
  leafAccounts,
  suggestedExpenseAccountId,
  suggestedIncomeAccountId,
  suggestedSettlementAccountId,
  templateCoaOptionLabel,
} from '@/lib/coaDefaults'

type Account = { id: number; code: string; name: string; book?: string; is_group?: boolean }

const META: Record<string, { title: string; subtitle: string; mode: 'payment' | 'receipt' | 'contra' | 'journal'; book?: string }> = {
  cash_payment: { title: 'Cash Payment Voucher', subtitle: 'Pay from cash. Debit the expense or asset; cash is credited.', mode: 'payment', book: 'cash' },
  bank_payment: { title: 'Bank Payment Voucher', subtitle: 'Pay from bank. Debit the expense or asset; bank is credited.', mode: 'payment', book: 'bank' },
  cash_receipt: { title: 'Cash Receipt Voucher', subtitle: 'Receive into cash. Credit income or receivable; cash is debited.', mode: 'receipt', book: 'cash' },
  bank_receipt: { title: 'Bank Receipt Voucher', subtitle: 'Receive into bank. Credit income or receivable; bank is debited.', mode: 'receipt', book: 'bank' },
  contra: { title: 'Contra Voucher', subtitle: 'Transfer between cash and bank.', mode: 'contra' },
  journal: { title: 'Journal Voucher', subtitle: 'Debit and credit must balance.', mode: 'journal' },
}

function emptyLine() {
  return { account_id: '', debit: '', credit: '', description: '' }
}

export default function VoucherEntryPage({ voucherType }: { voucherType: string }) {
  const router = useRouter()
  const meta = META[voucherType] || META.journal
  const [accounts, setAccounts] = useState<Account[]>([])
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [description, setDescription] = useState('')
  const [reference, setReference] = useState('')
  const [lines, setLines] = useState([emptyLine(), emptyLine()])
  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const leaves = useMemo(() => accounts.filter((a) => !a.is_group), [accounts])
  const cashBank = useMemo(() => leaves.filter((a) => a.book === 'cash' || a.book === 'bank'), [leaves])

  useEffect(() => {
    apiClient
      .get('/accounts/chart-of-accounts')
      .then((res) => {
        const flat = leafAccounts(res.data.flat || res.data.accounts || [])
        setAccounts(
          flat.map((a) => ({
            id: a.id,
            code: a.account_code || a.code || '',
            name: a.account_name || a.name || '',
            book: a.book,
            is_group: a.is_group,
          }))
        )
        // Prefill first line with recommended expense/income (editable).
        const picks = flat
        if (meta.mode === 'payment') {
          const id = suggestedExpenseAccountId(picks, 'general')
          if (id) setLines((prev) => prev.map((line, i) => (i === 0 && !line.account_id ? { ...line, account_id: id } : line)))
        } else if (meta.mode === 'receipt') {
          const id = suggestedIncomeAccountId(picks, 'other')
          if (id) setLines((prev) => prev.map((line, i) => (i === 0 && !line.account_id ? { ...line, account_id: id } : line)))
        } else if (meta.mode === 'contra') {
          const bank = suggestedSettlementAccountId(picks)
          const cash = picks.find((a) => a.book === 'cash')
          if (bank && !fromId) setFromId(bank)
          if (cash && !toId) setToId(String(cash.id))
        }
      })
      .catch(() => setAccounts([]))
  }, [voucherType])

  const updateLine = (index: number, key: string, value: string) => {
    setLines((prev) => prev.map((line, i) => (i === index ? { ...line, [key]: value } : line)))
  }

  const debitTotal = lines.reduce((s, l) => s + Number(l.debit || 0), 0)
  const creditTotal = lines.reduce((s, l) => s + Number(l.credit || 0), 0)

  const submit = async (post: boolean) => {
    setSaving(true)
    setError('')
    try {
      let payloadLines: any[] = []
      if (meta.mode === 'contra') {
        if (!fromId || !toId || !amount) throw new Error('From account, to account, and amount are required')
        payloadLines = [
          { account_id: Number(fromId), credit: Number(amount), debit: 0, description },
          { account_id: Number(toId), debit: Number(amount), credit: 0, description },
        ]
      } else if (meta.mode === 'journal') {
        payloadLines = lines
          .filter((l) => l.account_id && (l.debit || l.credit))
          .map((l) => ({
            account_id: Number(l.account_id),
            debit: Number(l.debit || 0),
            credit: Number(l.credit || 0),
            description: l.description,
          }))
      } else {
        payloadLines = lines
          .filter((l) => l.account_id && (l.debit || l.credit))
          .map((l) => {
            const amt = Number(l.debit || l.credit || 0)
            return {
              account_id: Number(l.account_id),
              debit: meta.mode === 'payment' ? amt : 0,
              credit: meta.mode === 'receipt' ? amt : 0,
              description: l.description,
            }
          })
      }
      const res = await apiClient.post('/accounts/vouchers', {
        voucher_type: voucherType,
        date,
        description,
        reference,
        lines: payloadLines,
        post,
      })
      router.push(`/accounts/vouchers/${res.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">{meta.title}</h1>
          <p className="mt-1 text-gray-600">{meta.subtitle}</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-4">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Date</span>
              <input type="date" className="w-full rounded-lg border px-3 py-2" value={date} onChange={(e) => setDate(e.target.value)} />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Reference</span>
              <input className="w-full rounded-lg border px-3 py-2" value={reference} onChange={(e) => setReference(e.target.value)} />
            </label>
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Narration</span>
              <input className="w-full rounded-lg border px-3 py-2" value={description} onChange={(e) => setDescription(e.target.value)} />
            </label>
          </div>

          {meta.mode === 'contra' ? (
            <div className="mt-4 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-3">
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">From (credit)</span>
                <select className="w-full rounded-lg border px-3 py-2" value={fromId} onChange={(e) => setFromId(e.target.value)}>
                  <option value="">Select…</option>
                  {cashBank.map((a) => (
                    <option key={a.id} value={a.id}>{a.code} {a.name}</option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">To (debit)</span>
                <select className="w-full rounded-lg border px-3 py-2" value={toId} onChange={(e) => setToId(e.target.value)}>
                  <option value="">Select…</option>
                  {cashBank.map((a) => (
                    <option key={a.id} value={a.id}>{a.code} {a.name}</option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="mb-1 block text-slate-600">Amount</span>
                <input type="number" min="0" step="0.01" className="w-full rounded-lg border px-3 py-2" value={amount} onChange={(e) => setAmount(e.target.value)} />
              </label>
            </div>
          ) : (
            <div className="mt-4 overflow-hidden rounded-xl border bg-white">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Account</th>
                    {meta.mode === 'journal' ? (
                      <>
                        <th className="px-3 py-2">Debit</th>
                        <th className="px-3 py-2">Credit</th>
                      </>
                    ) : (
                      <th className="px-3 py-2">Amount</th>
                    )}
                    <th className="px-3 py-2">Narration</th>
                    <th className="px-3 py-2" />
                  </tr>
                </thead>
                <tbody>
                  {lines.map((line, index) => (
                    <tr key={index} className="border-t">
                      <td className="px-3 py-2">
                        <select
                          className="w-full rounded border px-2 py-1"
                          value={line.account_id}
                          onChange={(e) => updateLine(index, 'account_id', e.target.value)}
                        >
                          <option value="">
                            {meta.mode === 'payment'
                              ? templateCoaOptionLabel(COA.GENERAL_OPEX, leaves.map((a) => ({ id: a.id, account_code: a.code, account_name: a.name })))
                              : meta.mode === 'receipt'
                                ? templateCoaOptionLabel(COA.OTHER_INCOME, leaves.map((a) => ({ id: a.id, account_code: a.code, account_name: a.name })))
                                : 'Select account…'}
                          </option>
                          {leaves.map((a) => (
                            <option key={a.id} value={a.id}>{a.code} {a.name}</option>
                          ))}
                        </select>
                      </td>
                      {meta.mode === 'journal' ? (
                        <>
                          <td className="px-3 py-2">
                            <input type="number" min="0" step="0.01" className="w-full rounded border px-2 py-1" value={line.debit} onChange={(e) => updateLine(index, 'debit', e.target.value)} />
                          </td>
                          <td className="px-3 py-2">
                            <input type="number" min="0" step="0.01" className="w-full rounded border px-2 py-1" value={line.credit} onChange={(e) => updateLine(index, 'credit', e.target.value)} />
                          </td>
                        </>
                      ) : (
                        <td className="px-3 py-2">
                          <input type="number" min="0" step="0.01" className="w-full rounded border px-2 py-1" value={line.debit} onChange={(e) => updateLine(index, 'debit', e.target.value)} />
                        </td>
                      )}
                      <td className="px-3 py-2">
                        <input className="w-full rounded border px-2 py-1" value={line.description} onChange={(e) => updateLine(index, 'description', e.target.value)} />
                      </td>
                      <td className="px-3 py-2">
                        <button type="button" onClick={() => setLines((prev) => prev.filter((_, i) => i !== index))} className="text-red-600">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex items-center justify-between border-t px-3 py-2 text-sm">
                <button type="button" onClick={() => setLines((prev) => [...prev, emptyLine()])} className="inline-flex items-center gap-1 text-indigo-700">
                  <Plus className="h-4 w-4" /> Add line
                </button>
                {meta.mode === 'journal' && (
                  <span className={debitTotal === creditTotal ? 'text-emerald-700' : 'text-red-600'}>
                    Debit {formatMoney(debitTotal)} · Credit {formatMoney(creditTotal)}
                  </span>
                )}
                {meta.mode !== 'journal' && (
                  <span className="text-slate-500">{meta.book} account is posted automatically</span>
                )}
              </div>
            </div>
          )}

          <div className="mt-4 flex gap-2">
            <button type="button" disabled={saving} onClick={() => submit(true)} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50">
              {saving ? 'Saving…' : 'Post voucher'}
            </button>
            <button type="button" disabled={saving} onClick={() => submit(false)} className="rounded-lg border bg-white px-4 py-2 text-sm">
              Save draft
            </button>
            <button type="button" onClick={() => router.push('/accounts/vouchers')} className="rounded-lg border bg-white px-4 py-2 text-sm">
              Cancel
            </button>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
