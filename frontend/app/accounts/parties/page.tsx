'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

type Party = {
  id: number
  code: string
  name: string
  party_type: string
  control_code: string
  control_name: string
  opening_balance: number
  opening_balance_as_of: string | null
  balance: number
  is_active: boolean
}

const TYPE_LABELS: Record<string, string> = {
  guest: 'Guest',
  customer: 'Customer',
  company: 'Company',
  vendor: 'Vendor',
  supplier: 'Supplier',
  employee: 'Employee',
  loan_counterparty: 'Loan party',
  other: 'Other',
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function PartyLedgersPage() {
  const router = useRouter()
  const [parties, setParties] = useState<Party[]>([])
  const [types, setTypes] = useState<{ value: string; label: string }[]>([])
  const [partyType, setPartyType] = useState('')
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    name: '',
    party_type: 'customer',
    opening_balance: '0',
    opening_balance_as_of: today(),
  })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (partyType) params.set('party_type', partyType)
    if (search) params.set('search', search)
    apiClient
      .get(`/accounts/parties?${params.toString()}`)
      .then((res) => {
        setParties(res.data.parties || [])
        setTypes(res.data.party_types || [])
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [partyType])

  useEffect(() => {
    const t = setTimeout(() => load(), 250)
    return () => clearTimeout(t)
  }, [search])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const opening = Number(form.opening_balance || 0)
      await apiClient.post('/accounts/parties', {
        name: form.name,
        party_type: form.party_type,
        opening_balance: opening,
        opening_balance_as_of: opening ? form.opening_balance_as_of : null,
      })
      setForm({ name: '', party_type: form.party_type, opening_balance: '0', opening_balance_as_of: today() })
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Party Ledgers</h1>
              <p className="mt-1 text-gray-600">
                Subsidiary ledgers for guests, customers, vendors, employees, and loan parties. Click a row for the statement.
              </p>
            </div>
            <div className="flex gap-2 text-sm">
              <Link href="/accounts/parties/aging" className="rounded-lg border bg-white px-3 py-2 text-indigo-700">
                Aging
              </Link>
              <Link href="/accounts/parties/reconcile" className="rounded-lg border bg-white px-3 py-2 text-indigo-700">
                Reconcile
              </Link>
            </div>
          </div>

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <form onSubmit={submit} className="mt-6 grid gap-3 rounded-xl border bg-white p-4 sm:grid-cols-2 lg:grid-cols-5">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Name *</span>
              <input
                className="w-full rounded-lg border px-3 py-2"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Type</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={form.party_type}
                onChange={(e) => setForm({ ...form, party_type: e.target.value })}
              >
                {(types.length ? types : Object.entries(TYPE_LABELS).map(([value, label]) => ({ value, label }))).map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Opening balance</span>
              <input
                type="number"
                step="0.01"
                className="w-full rounded-lg border px-3 py-2"
                value={form.opening_balance}
                onChange={(e) => setForm({ ...form, opening_balance: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">As of</span>
              <input
                type="date"
                className="w-full rounded-lg border px-3 py-2"
                value={form.opening_balance_as_of}
                onChange={(e) => setForm({ ...form, opening_balance_as_of: e.target.value })}
              />
            </label>
            <div className="flex items-end">
              <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50">
                {saving ? 'Saving…' : 'Add party'}
              </button>
            </div>
          </form>

          <div className="mt-4 flex flex-wrap gap-3">
            <select className="rounded-lg border bg-white px-3 py-2 text-sm" value={partyType} onChange={(e) => setPartyType(e.target.value)}>
              <option value="">All types</option>
              {(types.length ? types : Object.entries(TYPE_LABELS).map(([value, label]) => ({ value, label }))).map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
            <input
              className="min-w-[220px] rounded-lg border bg-white px-3 py-2 text-sm"
              placeholder="Search code or name"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="mt-4 overflow-auto rounded-xl border bg-white">
            {loading ? (
              <p className="p-8 text-center text-slate-500">Loading…</p>
            ) : parties.length === 0 ? (
              <p className="p-8 text-center text-slate-500">No party accounts yet. They are created when you post AR/AP/folio/purchases, or add one above.</p>
            ) : (
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Code</th>
                    <th className="px-3 py-2">Name</th>
                    <th className="px-3 py-2">Type</th>
                    <th className="px-3 py-2">Control GL</th>
                    <th className="px-3 py-2 text-right">Opening</th>
                    <th className="px-3 py-2 text-right">Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {parties.map((p) => (
                    <tr
                      key={p.id}
                      className="cursor-pointer border-t hover:bg-indigo-50/60"
                      onClick={() => router.push(`/accounts/parties/${p.id}`)}
                    >
                      <td className="px-3 py-2 font-medium text-indigo-700">{p.code}</td>
                      <td className="px-3 py-2">{p.name}</td>
                      <td className="px-3 py-2 capitalize">{TYPE_LABELS[p.party_type] || p.party_type}</td>
                      <td className="px-3 py-2">
                        {p.control_code} {p.control_name}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">{formatMoney(p.opening_balance)}</td>
                      <td className="px-3 py-2 text-right tabular-nums font-medium">{formatMoney(p.balance)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
