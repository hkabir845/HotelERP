'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

function monthStart() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function PartyLedgerDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id
  const [from, setFrom] = useState(monthStart())
  const [to, setTo] = useState(today())
  const [party, setParty] = useState<any>(null)
  const [entries, setEntries] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [ob, setOb] = useState({ opening_balance: '', opening_balance_as_of: today() })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams({ from, to })
    apiClient
      .get(`/accounts/parties/${id}?${params.toString()}`)
      .then((res) => {
        setParty(res.data.party)
        setEntries(res.data.entries || [])
        setOb({
          opening_balance: String(res.data.party?.opening_balance ?? 0),
          opening_balance_as_of: res.data.party?.opening_balance_as_of || today(),
        })
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (id) load()
  }, [id])

  const saveOpening = async () => {
    setSaving(true)
    setError('')
    try {
      const res = await apiClient.patch(`/accounts/parties/${id}`, {
        opening_balance: Number(ob.opening_balance || 0),
        opening_balance_as_of: Number(ob.opening_balance || 0) ? ob.opening_balance_as_of : null,
      })
      setParty(res.data)
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Update failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <button type="button" onClick={() => router.push('/accounts/parties')} className="text-sm text-indigo-700">
            Back to party ledgers
          </button>
          {error && <p className="mt-3 text-red-600">{error}</p>}
          {loading || !party ? (
            <p className="mt-6 text-slate-500">Loading…</p>
          ) : (
            <>
              <h1 className="mt-4 text-3xl font-bold text-gray-900">
                {party.code} — {party.name}
              </h1>
              <p className="mt-1 text-gray-600 capitalize">
                {party.party_type?.replace('_', ' ')} · Control {party.control_code} {party.control_name} · Balance{' '}
                <span className="font-semibold text-gray-900">{formatMoney(party.balance)}</span>
              </p>

              <div className="mt-4 flex flex-wrap items-end gap-3 rounded-xl border bg-white p-4">
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">From</span>
                  <input type="date" className="rounded-lg border px-3 py-2" value={from} onChange={(e) => setFrom(e.target.value)} />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">To</span>
                  <input type="date" className="rounded-lg border px-3 py-2" value={to} onChange={(e) => setTo(e.target.value)} />
                </label>
                <button type="button" onClick={load} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">
                  Run
                </button>
                <div className="mx-2 hidden h-8 w-px bg-slate-200 sm:block" />
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Opening</span>
                  <input
                    type="number"
                    step="0.01"
                    className="w-28 rounded-lg border px-3 py-2"
                    value={ob.opening_balance}
                    onChange={(e) => setOb({ ...ob, opening_balance: e.target.value })}
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">As of</span>
                  <input
                    type="date"
                    className="rounded-lg border px-3 py-2"
                    value={ob.opening_balance_as_of}
                    onChange={(e) => setOb({ ...ob, opening_balance_as_of: e.target.value })}
                  />
                </label>
                <button type="button" disabled={saving} onClick={saveOpening} className="rounded-lg border px-3 py-2 text-sm">
                  {saving ? 'Saving…' : 'Update opening'}
                </button>
              </div>

              <div className="mt-4 overflow-auto rounded-xl border bg-white">
                {entries.length === 0 ? (
                  <p className="p-8 text-center text-slate-500">No movements in this period.</p>
                ) : (
                  <table className="min-w-full text-sm">
                    <thead className="bg-slate-50 text-left text-slate-600">
                      <tr>
                        <th className="px-3 py-2">Date</th>
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Narration</th>
                        <th className="px-3 py-2 text-right">Debit</th>
                        <th className="px-3 py-2 text-right">Credit</th>
                        <th className="px-3 py-2 text-right">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {entries.map((row) => (
                        <tr key={row.id} className="border-t">
                          <td className="px-3 py-2">{row.date}</td>
                          <td className="px-3 py-2">
                            {row.journal_entry_id ? (
                              <Link href={`/accounts/vouchers/${row.journal_entry_id}`} className="text-indigo-700 hover:underline">
                                {row.voucher}
                              </Link>
                            ) : (
                              row.voucher || '—'
                            )}
                          </td>
                          <td className="px-3 py-2">{row.narration || '—'}</td>
                          <td className="px-3 py-2 text-right tabular-nums">{row.debit ? formatMoney(row.debit) : ''}</td>
                          <td className="px-3 py-2 text-right tabular-nums">{row.credit ? formatMoney(row.credit) : ''}</td>
                          <td className="px-3 py-2 text-right tabular-nums">{formatMoney(row.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
