'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import {
  Calculator,
  Landmark,
  Plus,
  RefreshCw,
  Search,
  Users,
  X,
} from 'lucide-react'

type Tab = 'loans' | 'counterparties'

interface AccountOpt {
  id: number
  code: string
  name: string
  account_type: string
  book: string
}

interface Counterparty {
  id: number
  code: string
  name: string
  role_type: string
  party_kind: string
  opening_balance_type: string
  opening_balance: number
  opening_balance_as_of: string | null
  phone: string
  email: string
  notes: string
  is_active: boolean
}

interface LoanRow {
  id: number
  loan_no: string
  direction: string
  status: string
  counterparty_id: number
  counterparty_code: string
  counterparty_name: string
  title: string
  agreement_no: string
  principal_account_id: number
  settlement_account_id: number
  interest_account_id: number | null
  interest_accrual_account_id: number | null
  sanction_amount: number
  outstanding_principal: number
  total_disbursed: number
  total_repaid_principal: number
  start_date: string | null
  maturity_date: string | null
  annual_interest_rate: number
  term_months: number | null
  banking_model: string
  product_type: string
  interest_bearing: boolean
  is_islamic_financing?: boolean
  charge_label?: string
  islamic_contract_variant?: string
  parent_loan_id?: number | null
  parent_loan_no?: string
  deal_reference?: string
  notes: string
  disbursements?: any[]
  repayments?: any[]
  interest_accruals?: any[]
}

const PRODUCT_OPTIONS = [
  { value: 'general', label: 'General / corporate' },
  { value: 'individual', label: 'Individual loan' },
  { value: 'term_loan', label: 'Term loan' },
  { value: 'business_line', label: 'Business line' },
  { value: 'islamic_facility', label: 'Islamic facility (limit only)' },
  { value: 'islamic_deal', label: 'Islamic deal (under facility)' },
]

const ISLAMIC_CONTRACTS = [
  { value: '', label: 'General Islamic financing' },
  { value: 'murabaha', label: 'Murabaha' },
  { value: 'ijara', label: 'Ijara' },
  { value: 'musharaka', label: 'Musharaka' },
  { value: 'mudaraba', label: 'Mudaraba' },
  { value: 'bai_muajjal', label: 'Bai Muajjal' },
  { value: 'istisna', label: 'Istisna' },
]

const emptyLoanForm = {
  loan_no: '',
  direction: 'borrowed',
  counterparty_id: '',
  title: '',
  agreement_no: '',
  sanction_amount: '',
  annual_interest_rate: '',
  term_months: '',
  start_date: '',
  maturity_date: '',
  principal_account_id: '',
  settlement_account_id: '',
  interest_account_id: '',
  interest_accrual_account_id: '',
  banking_model: 'conventional',
  product_type: 'general',
  interest_bearing: true,
  islamic_contract_variant: '',
  parent_loan_id: '',
  deal_reference: '',
  notes: '',
}

function bankingLabel(bm: string) {
  return bm === 'islamic' ? 'Islamic' : 'Bank'
}

function productLabel(pt: string) {
  return PRODUCT_OPTIONS.find((p) => p.value === pt)?.label || pt
}

export default function CorporateLoansPage() {
  const [tab, setTab] = useState<Tab>('loans')
  const [loading, setLoading] = useState(true)
  const [loans, setLoans] = useState<LoanRow[]>([])
  const [counterparties, setCounterparties] = useState<Counterparty[]>([])
  const [accounts, setAccounts] = useState<AccountOpt[]>([])
  const [defaults, setDefaults] = useState<any>({})
  const [q, setQ] = useState('')
  const [directionFilter, setDirectionFilter] = useState('all')
  const [bankingFilter, setBankingFilter] = useState('all')
  const [productFilter, setProductFilter] = useState('all')
  const [interestFilter, setInterestFilter] = useState('all')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [detail, setDetail] = useState<LoanRow | null>(null)
  const [error, setError] = useState('')
  const [showLoanForm, setShowLoanForm] = useState(false)
  const [showCpForm, setShowCpForm] = useState(false)
  const [loanForm, setLoanForm] = useState({ ...emptyLoanForm })
  const [cpForm, setCpForm] = useState({
    code: '',
    name: '',
    role_type: 'bank',
    party_kind: 'lender',
    opening_balance_type: 'zero',
    opening_balance: '',
    opening_balance_as_of: '',
    phone: '',
    email: '',
    notes: '',
  })
  const [actionForm, setActionForm] = useState({
    amount: '',
    date: new Date().toISOString().slice(0, 10),
    principal_amount: '',
    interest_amount: '',
    reference: '',
    memo: '',
  })
  const [schedule, setSchedule] = useState<any[]>([])
  const [busy, setBusy] = useState(false)

  const islamicFacilities = useMemo(
    () =>
      loans.filter(
        (l) =>
          l.product_type === 'islamic_facility' &&
          l.direction === loanForm.direction &&
          l.status !== 'closed',
      ),
    [loans, loanForm.direction],
  )

  const chargeWord = detail?.is_islamic_financing
    ? 'Profit'
    : detail && !detail.interest_bearing
      ? 'Interest-free'
      : 'Interest'

  const loadMeta = useCallback(async () => {
    const res = await apiClient.get('/accounts/loans/meta')
    setAccounts(res.data.accounts || [])
    setDefaults(res.data.defaults || {})
  }, [])

  const loadLoans = useCallback(async () => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (directionFilter !== 'all') params.set('direction', directionFilter)
    if (bankingFilter !== 'all') params.set('banking_model', bankingFilter)
    if (productFilter !== 'all') params.set('product_type', productFilter)
    if (interestFilter === 'with') params.set('interest_bearing', '1')
    if (interestFilter === 'without') params.set('interest_bearing', '0')
    const res = await apiClient.get(`/accounts/loans?${params}`)
    setLoans(res.data || [])
  }, [q, directionFilter, bankingFilter, productFilter, interestFilter])

  const loadCounterparties = useCallback(async () => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    const res = await apiClient.get(`/accounts/loans/counterparties?${params}`)
    setCounterparties(res.data || [])
  }, [q])

  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      await loadMeta()
      await Promise.all([loadLoans(), loadCounterparties()])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load loans')
    } finally {
      setLoading(false)
    }
  }, [loadMeta, loadLoans, loadCounterparties])

  useEffect(() => {
    refresh()
  }, [refresh])

  const openDetail = async (id: number) => {
    setSelectedId(id)
    try {
      const res = await apiClient.get(`/accounts/loans/${id}`)
      setDetail(res.data)
      setSchedule([])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load loan')
    }
  }

  const applyDirectionDefaults = (direction: string, form = loanForm) => {
    const d = defaults?.[direction] || {}
    const bank =
      accounts.find((a) => a.book === 'bank') || accounts.find((a) => a.book === 'cash')
    // Prefer built-in hotel COA codes when meta defaults are empty.
    const bySuffix = (suffix: string) =>
      accounts.find((a) => String(a.code || '') === suffix) ||
      accounts.find((a) => String(a.code || '').endsWith(`-${suffix}`))
    const borrowedPrincipal = bySuffix('2410')
    const lentPrincipal = bySuffix('1160')
    const interestExp = bySuffix('6620')
    const interestInc = bySuffix('4410')
    const principal =
      direction === 'lent'
        ? lentPrincipal || bySuffix(String(d.principal_account_id || ''))
        : borrowedPrincipal
    const interest = direction === 'lent' ? interestInc : interestExp
    setLoanForm({
      ...form,
      direction,
      principal_account_id: String(
        d.principal_account_id || principal?.id || form.principal_account_id || ''
      ),
      interest_account_id: String(
        d.interest_account_id || interest?.id || form.interest_account_id || ''
      ),
      interest_accrual_account_id: String(
        d.interest_accrual_account_id || form.interest_accrual_account_id || ''
      ),
      settlement_account_id: String(bank?.id || form.settlement_account_id || ''),
    })
  }

  const patchLoanForm = (patch: Partial<typeof emptyLoanForm>) => {
    setLoanForm((prev) => {
      const next = { ...prev, ...patch }
      if (patch.product_type === 'islamic_facility' || patch.product_type === 'islamic_deal') {
        next.banking_model = 'islamic'
      }
      if (patch.banking_model === 'conventional') {
        next.islamic_contract_variant = ''
        if (next.product_type === 'islamic_facility' || next.product_type === 'islamic_deal') {
          next.product_type = 'general'
          next.parent_loan_id = ''
        }
      }
      if (patch.interest_bearing === false) {
        next.annual_interest_rate = '0'
      }
      if (patch.product_type && patch.product_type !== 'islamic_deal') {
        next.parent_loan_id = ''
      }
      return next
    })
  }

  const createLoan = async () => {
    setBusy(true)
    setError('')
    try {
      if (loanForm.product_type === 'islamic_deal' && !loanForm.parent_loan_id) {
        setError('Islamic deal requires a parent Islamic facility')
        setBusy(false)
        return
      }
      const payload: any = {
        ...loanForm,
        counterparty_id: Number(loanForm.counterparty_id),
        principal_account_id: Number(loanForm.principal_account_id),
        settlement_account_id: Number(loanForm.settlement_account_id),
        interest_account_id: loanForm.interest_bearing && loanForm.interest_account_id
          ? Number(loanForm.interest_account_id)
          : null,
        interest_accrual_account_id:
          loanForm.interest_bearing && loanForm.interest_accrual_account_id
            ? Number(loanForm.interest_accrual_account_id)
            : null,
        sanction_amount: Number(loanForm.sanction_amount || 0),
        annual_interest_rate: loanForm.interest_bearing
          ? Number(loanForm.annual_interest_rate || 0)
          : 0,
        interest_bearing: loanForm.interest_bearing,
        term_months: loanForm.term_months ? Number(loanForm.term_months) : null,
        start_date: loanForm.start_date || null,
        maturity_date: loanForm.maturity_date || null,
        parent_loan_id:
          loanForm.product_type === 'islamic_deal' ? Number(loanForm.parent_loan_id) : null,
      }
      const res = await apiClient.post('/accounts/loans', payload)
      setShowLoanForm(false)
      setLoanForm({ ...emptyLoanForm })
      await loadLoans()
      await openDetail(res.data.id)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not create loan')
    } finally {
      setBusy(false)
    }
  }

  const createCounterparty = async () => {
    setBusy(true)
    setError('')
    try {
      await apiClient.post('/accounts/loans/counterparties', {
        ...cpForm,
        opening_balance: Number(cpForm.opening_balance || 0),
        opening_balance_as_of: cpForm.opening_balance_as_of || null,
        post_opening: true,
      })
      setShowCpForm(false)
      setCpForm({
        code: '',
        name: '',
        role_type: 'bank',
        party_kind: 'lender',
        opening_balance_type: 'zero',
        opening_balance: '',
        opening_balance_as_of: '',
        phone: '',
        email: '',
        notes: '',
      })
      await loadCounterparties()
      setTab('counterparties')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not create counterparty')
    } finally {
      setBusy(false)
    }
  }

  const runDisburse = async () => {
    if (!detail) return
    if (detail.product_type === 'islamic_facility') {
      setError('Islamic facility is a limit only — create an Islamic deal and disburse there')
      return
    }
    setBusy(true)
    setError('')
    try {
      await apiClient.post(`/accounts/loans/${detail.id}/disburse`, {
        amount: Number(actionForm.amount),
        disbursement_date: actionForm.date,
        reference: actionForm.reference,
        memo: actionForm.memo,
      })
      setActionForm((f) => ({ ...f, amount: '', reference: '', memo: '' }))
      await openDetail(detail.id)
      await loadLoans()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Disbursement failed')
    } finally {
      setBusy(false)
    }
  }

  const runRepay = async () => {
    if (!detail) return
    setBusy(true)
    setError('')
    try {
      const payload: any = {
        amount: Number(actionForm.amount),
        repayment_date: actionForm.date,
        reference: actionForm.reference,
        memo: actionForm.memo,
      }
      if (
        detail.interest_bearing &&
        (actionForm.principal_amount !== '' || actionForm.interest_amount !== '')
      ) {
        payload.principal_amount = Number(actionForm.principal_amount || 0)
        payload.interest_amount = Number(actionForm.interest_amount || 0)
      }
      await apiClient.post(`/accounts/loans/${detail.id}/repay`, payload)
      setActionForm((f) => ({
        ...f,
        amount: '',
        principal_amount: '',
        interest_amount: '',
        reference: '',
        memo: '',
      }))
      await openDetail(detail.id)
      await loadLoans()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Repayment failed')
    } finally {
      setBusy(false)
    }
  }

  const runAccrue = async () => {
    if (!detail) return
    if (!detail.interest_bearing) {
      setError('This loan is without interest — accrual is not allowed')
      return
    }
    setBusy(true)
    setError('')
    try {
      await apiClient.post(`/accounts/loans/${detail.id}/accrue`, {
        amount: actionForm.amount ? Number(actionForm.amount) : undefined,
        accrual_date: actionForm.date,
        memo: actionForm.memo,
      })
      setActionForm((f) => ({ ...f, amount: '', memo: '' }))
      await openDetail(detail.id)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Accrual failed')
    } finally {
      setBusy(false)
    }
  }

  const loadSchedule = async () => {
    if (!detail) return
    try {
      const res = await apiClient.get(`/accounts/loans/${detail.id}/schedule`)
      setSchedule(res.data.rows || [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Schedule failed')
    }
  }

  const totals = useMemo(() => {
    const borrowed = loans
      .filter((l) => l.direction === 'borrowed')
      .reduce((s, l) => s + (l.outstanding_principal || 0), 0)
    const lent = loans
      .filter((l) => l.direction === 'lent')
      .reduce((s, l) => s + (l.outstanding_principal || 0), 0)
    return { borrowed, lent, count: loans.length }
  }, [loans])

  const accountLabel = (id?: number | null) => {
    if (!id) return '—'
    const a = accounts.find((x) => x.id === id)
    return a ? `${a.code} — ${a.name}` : `#${id}`
  }

  const rateLabel = (row: LoanRow) => {
    if (!row.interest_bearing) return 'Interest-free'
    if (row.is_islamic_financing) return `${row.annual_interest_rate}% profit`
    return `${row.annual_interest_rate}%`
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Landmark className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Corporate Loans</h1>
                  <p className="text-gray-600 mt-1">
                    Bank &amp; Islamic banking · Individual loans with/without interest · GL posting
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={refresh}
                  className="inline-flex items-center gap-2 px-3 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50"
                >
                  <RefreshCw className="h-4 w-4" /> Refresh
                </button>
                {tab === 'loans' ? (
                  <button
                    onClick={() => {
                      const form = { ...emptyLoanForm }
                      setShowLoanForm(true)
                      setTimeout(() => applyDirectionDefaults('borrowed', form), 0)
                    }}
                    className="inline-flex items-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
                  >
                    <Plus className="h-4 w-4" /> New loan
                  </button>
                ) : (
                  <button
                    onClick={() => setShowCpForm(true)}
                    className="inline-flex items-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
                  >
                    <Plus className="h-4 w-4" /> New counterparty
                  </button>
                )}
              </div>
            </div>

            {error && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-lg border p-4">
                <div className="text-sm text-gray-500">Facilities</div>
                <div className="text-2xl font-semibold mt-1">{totals.count}</div>
              </div>
              <div className="bg-white rounded-lg border p-4">
                <div className="text-sm text-gray-500">Borrowed O/S</div>
                <div className="text-2xl font-semibold mt-1 text-rose-700">
                  {formatMoney(totals.borrowed)}
                </div>
              </div>
              <div className="bg-white rounded-lg border p-4">
                <div className="text-sm text-gray-500">Lent O/S</div>
                <div className="text-2xl font-semibold mt-1 text-emerald-700">
                  {formatMoney(totals.lent)}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 mb-4">
              <div className="flex bg-white border rounded-lg p-1">
                <button
                  onClick={() => setTab('loans')}
                  className={`px-3 py-1.5 text-sm rounded-md ${
                    tab === 'loans' ? 'bg-indigo-600 text-white' : 'text-gray-700'
                  }`}
                >
                  Loans
                </button>
                <button
                  onClick={() => setTab('counterparties')}
                  className={`px-3 py-1.5 text-sm rounded-md inline-flex items-center gap-1 ${
                    tab === 'counterparties' ? 'bg-indigo-600 text-white' : 'text-gray-700'
                  }`}
                >
                  <Users className="h-3.5 w-3.5" /> Counterparties
                </button>
              </div>
              <div className="relative flex-1 min-w-[180px]">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Search…"
                  className="w-full pl-9 pr-3 py-2 border rounded-lg bg-white text-sm"
                />
              </div>
              {tab === 'loans' && (
                <>
                  <select
                    value={directionFilter}
                    onChange={(e) => setDirectionFilter(e.target.value)}
                    className="border rounded-lg px-3 py-2 bg-white text-sm"
                  >
                    <option value="all">All directions</option>
                    <option value="borrowed">Borrowed</option>
                    <option value="lent">Lent</option>
                  </select>
                  <select
                    value={bankingFilter}
                    onChange={(e) => setBankingFilter(e.target.value)}
                    className="border rounded-lg px-3 py-2 bg-white text-sm"
                  >
                    <option value="all">Bank + Islamic</option>
                    <option value="conventional">Bank only</option>
                    <option value="islamic">Islamic only</option>
                  </select>
                  <select
                    value={productFilter}
                    onChange={(e) => setProductFilter(e.target.value)}
                    className="border rounded-lg px-3 py-2 bg-white text-sm"
                  >
                    <option value="all">All products</option>
                    {PRODUCT_OPTIONS.map((p) => (
                      <option key={p.value} value={p.value}>
                        {p.label}
                      </option>
                    ))}
                  </select>
                  <select
                    value={interestFilter}
                    onChange={(e) => setInterestFilter(e.target.value)}
                    className="border rounded-lg px-3 py-2 bg-white text-sm"
                  >
                    <option value="all">With + without interest</option>
                    <option value="with">With interest / profit</option>
                    <option value="without">Without interest</option>
                  </select>
                </>
              )}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
              <div className="xl:col-span-3 bg-white rounded-lg border overflow-hidden">
                {loading ? (
                  <div className="p-8 text-center text-gray-500">Loading…</div>
                ) : tab === 'loans' ? (
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-left text-gray-600">
                      <tr>
                        <th className="px-4 py-3">Loan</th>
                        <th className="px-4 py-3">Banking / product</th>
                        <th className="px-4 py-3">Counterparty</th>
                        <th className="px-4 py-3">Interest</th>
                        <th className="px-4 py-3 text-right">Outstanding</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loans.map((l) => (
                        <tr
                          key={l.id}
                          onClick={() => openDetail(l.id)}
                          className={`border-t cursor-pointer hover:bg-indigo-50 ${
                            selectedId === l.id ? 'bg-indigo-50' : ''
                          }`}
                        >
                          <td className="px-4 py-3">
                            <div className="font-medium">{l.loan_no}</div>
                            <div className="text-xs text-gray-500 capitalize">
                              {l.direction} · {l.status}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-1">
                              <span
                                className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
                                  l.banking_model === 'islamic'
                                    ? 'bg-teal-100 text-teal-800'
                                    : 'bg-slate-100 text-slate-800'
                                }`}
                              >
                                {bankingLabel(l.banking_model)}
                              </span>
                              {l.product_type === 'individual' && (
                                <span className="inline-flex px-2 py-0.5 rounded-full text-xs bg-violet-100 text-violet-800">
                                  Individual
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {productLabel(l.product_type)}
                              {l.islamic_contract_variant
                                ? ` · ${l.islamic_contract_variant.replace(/_/g, ' ')}`
                                : ''}
                            </div>
                          </td>
                          <td className="px-4 py-3">{l.counterparty_name}</td>
                          <td className="px-4 py-3">
                            <span
                              className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
                                l.interest_bearing
                                  ? 'bg-amber-100 text-amber-900'
                                  : 'bg-gray-100 text-gray-700'
                              }`}
                            >
                              {rateLabel(l)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right font-medium">
                            {formatMoney(l.outstanding_principal)}
                          </td>
                        </tr>
                      ))}
                      {!loans.length && (
                        <tr>
                          <td colSpan={5} className="px-4 py-10 text-center text-gray-500">
                            No corporate loans yet
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                ) : (
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-left text-gray-600">
                      <tr>
                        <th className="px-4 py-3">Code</th>
                        <th className="px-4 py-3">Name</th>
                        <th className="px-4 py-3">Role</th>
                        <th className="px-4 py-3">Opening</th>
                        <th className="px-4 py-3">Active</th>
                      </tr>
                    </thead>
                    <tbody>
                      {counterparties.map((c) => (
                        <tr key={c.id} className="border-t">
                          <td className="px-4 py-3 font-medium">{c.code}</td>
                          <td className="px-4 py-3">{c.name}</td>
                          <td className="px-4 py-3">{c.role_type}</td>
                          <td className="px-4 py-3">
                            {c.opening_balance_type === 'zero'
                              ? '—'
                              : `${c.opening_balance_type} ${formatMoney(c.opening_balance)}`}
                          </td>
                          <td className="px-4 py-3">{c.is_active ? 'Yes' : 'No'}</td>
                        </tr>
                      ))}
                      {!counterparties.length && (
                        <tr>
                          <td colSpan={5} className="px-4 py-10 text-center text-gray-500">
                            No counterparties yet
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}
              </div>

              <div className="xl:col-span-2 bg-white rounded-lg border p-4 min-h-[420px]">
                {!detail ? (
                  <div className="h-full flex items-center justify-center text-gray-500 text-sm text-center px-4">
                    Select a loan to disburse, repay, accrue {chargeWord.toLowerCase()}, or preview
                    schedule
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Facility</div>
                      <div className="text-xl font-semibold">{detail.loan_no}</div>
                      <div className="text-sm text-gray-600">
                        {detail.counterparty_name} · {detail.direction} · {detail.status}
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
                            detail.banking_model === 'islamic'
                              ? 'bg-teal-100 text-teal-800'
                              : 'bg-slate-100 text-slate-800'
                          }`}
                        >
                          {bankingLabel(detail.banking_model)} banking
                        </span>
                        <span className="inline-flex px-2 py-0.5 rounded-full text-xs bg-indigo-50 text-indigo-800">
                          {productLabel(detail.product_type)}
                        </span>
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
                            detail.interest_bearing
                              ? 'bg-amber-100 text-amber-900'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {detail.interest_bearing ? `With ${chargeWord.toLowerCase()}` : 'Without interest'}
                        </span>
                      </div>
                      {detail.parent_loan_no && (
                        <div className="text-xs text-gray-500 mt-1">
                          Under facility {detail.parent_loan_no}
                          {detail.deal_reference ? ` · ${detail.deal_reference}` : ''}
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-gray-500">Sanction</div>
                        <div className="font-medium">{formatMoney(detail.sanction_amount)}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Outstanding</div>
                        <div className="font-medium">{formatMoney(detail.outstanding_principal)}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Disbursed</div>
                        <div className="font-medium">{formatMoney(detail.total_disbursed)}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">
                          {detail.interest_bearing ? `${chargeWord} / Term` : 'Term'}
                        </div>
                        <div className="font-medium">
                          {detail.interest_bearing
                            ? `${detail.annual_interest_rate}% / ${detail.term_months || '—'} mo`
                            : `${detail.term_months || '—'} mo · interest-free`}
                        </div>
                      </div>
                      <div className="col-span-2">
                        <div className="text-gray-500">Principal GL</div>
                        <div className="font-medium text-xs">
                          {accountLabel(detail.principal_account_id)}
                        </div>
                      </div>
                      <div className="col-span-2">
                        <div className="text-gray-500">Settlement GL</div>
                        <div className="font-medium text-xs">
                          {accountLabel(detail.settlement_account_id)}
                        </div>
                      </div>
                    </div>

                    {detail.product_type === 'islamic_facility' && (
                      <div className="text-sm text-sky-900 bg-sky-50 border border-sky-200 rounded-lg p-3">
                        This is a <strong>facility limit</strong> only. Add an{' '}
                        <strong>Islamic deal</strong> under it to disburse and repay.
                      </div>
                    )}

                    <div className="border-t pt-3 space-y-2">
                      <div className="text-sm font-medium">Posting</div>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="number"
                          placeholder="Amount"
                          value={actionForm.amount}
                          onChange={(e) => setActionForm({ ...actionForm, amount: e.target.value })}
                          className="border rounded-lg px-2 py-1.5 text-sm"
                        />
                        <input
                          type="date"
                          value={actionForm.date}
                          onChange={(e) => setActionForm({ ...actionForm, date: e.target.value })}
                          className="border rounded-lg px-2 py-1.5 text-sm"
                        />
                        {detail.interest_bearing && (
                          <>
                            <input
                              type="number"
                              placeholder="Principal (repay)"
                              value={actionForm.principal_amount}
                              onChange={(e) =>
                                setActionForm({ ...actionForm, principal_amount: e.target.value })
                              }
                              className="border rounded-lg px-2 py-1.5 text-sm"
                            />
                            <input
                              type="number"
                              placeholder={`${chargeWord} (repay)`}
                              value={actionForm.interest_amount}
                              onChange={(e) =>
                                setActionForm({ ...actionForm, interest_amount: e.target.value })
                              }
                              className="border rounded-lg px-2 py-1.5 text-sm"
                            />
                          </>
                        )}
                        <input
                          placeholder="Reference"
                          value={actionForm.reference}
                          onChange={(e) =>
                            setActionForm({ ...actionForm, reference: e.target.value })
                          }
                          className="border rounded-lg px-2 py-1.5 text-sm col-span-2"
                        />
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          disabled={busy || detail.product_type === 'islamic_facility'}
                          onClick={runDisburse}
                          className="px-3 py-1.5 text-sm rounded-lg bg-emerald-600 text-white disabled:opacity-50"
                        >
                          Disburse
                        </button>
                        <button
                          disabled={busy || detail.product_type === 'islamic_facility'}
                          onClick={runRepay}
                          className="px-3 py-1.5 text-sm rounded-lg bg-indigo-600 text-white disabled:opacity-50"
                        >
                          Repay
                        </button>
                        {detail.interest_bearing && (
                          <button
                            disabled={busy || detail.product_type === 'islamic_facility'}
                            onClick={runAccrue}
                            className="px-3 py-1.5 text-sm rounded-lg bg-amber-600 text-white disabled:opacity-50"
                          >
                            Accrue {chargeWord.toLowerCase()}
                          </button>
                        )}
                        <button
                          onClick={loadSchedule}
                          className="inline-flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg border"
                        >
                          <Calculator className="h-3.5 w-3.5" /> Schedule
                        </button>
                      </div>
                    </div>

                    {!!schedule.length && (
                      <div className="border-t pt-3 max-h-48 overflow-auto">
                        <div className="text-sm font-medium mb-2">Amortization preview</div>
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="text-left text-gray-500">
                              <th className="py-1">#</th>
                              <th>Due</th>
                              <th className="text-right">Payment</th>
                              <th className="text-right">Balance</th>
                            </tr>
                          </thead>
                          <tbody>
                            {schedule.map((r) => (
                              <tr key={r.installment} className="border-t">
                                <td className="py-1">{r.installment}</td>
                                <td>{r.due_date}</td>
                                <td className="text-right">{formatMoney(r.payment)}</td>
                                <td className="text-right">{formatMoney(r.balance)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    <div className="border-t pt-3 space-y-2 max-h-56 overflow-auto text-xs">
                      <div className="font-medium text-sm">History</div>
                      {(detail.disbursements || []).map((d: any) => (
                        <div key={`d-${d.id}`} className="flex justify-between gap-2">
                          <span>
                            Disburse {d.disbursement_date} {d.journal_entry_number || ''}
                          </span>
                          <span>{formatMoney(d.amount)}</span>
                        </div>
                      ))}
                      {(detail.repayments || []).map((r: any) => (
                        <div key={`r-${r.id}`} className="flex justify-between gap-2">
                          <span>
                            Repay {r.repayment_date}
                            {r.reversed_at ? ' (rev)' : ''} {r.journal_entry_number || ''}
                          </span>
                          <span>{formatMoney(r.amount)}</span>
                        </div>
                      ))}
                      {(detail.interest_accruals || []).map((a: any) => (
                        <div key={`a-${a.id}`} className="flex justify-between gap-2">
                          <span>
                            Accrue {a.accrual_date}
                            {a.reversed_at ? ' (rev)' : ''} {a.journal_entry_number || ''}
                          </span>
                          <span>{formatMoney(a.amount)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>

        {showLoanForm && (
          <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">New corporate loan</h2>
                <button onClick={() => setShowLoanForm(false)}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="col-span-2">
                  <span className="text-gray-600">Direction</span>
                  <div className="mt-1 grid grid-cols-2 gap-2">
                    {[
                      {
                        value: 'borrowed',
                        title: 'We borrowed',
                        sub: 'Liability — bank / Islamic / individual lender',
                      },
                      {
                        value: 'lent',
                        title: 'We lent',
                        sub: 'Receivable — advance to a party',
                      },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => applyDirectionDefaults(opt.value)}
                        className={`text-left rounded-lg border px-3 py-2 ${
                          loanForm.direction === opt.value
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        <div className="font-medium">{opt.title}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{opt.sub}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="col-span-2">
                  <span className="text-gray-600">Banking system</span>
                  <div className="mt-1 grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => patchLoanForm({ banking_model: 'conventional' })}
                      className={`text-left rounded-lg border px-3 py-2 ${
                        loanForm.banking_model === 'conventional'
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">Bank (conventional)</div>
                      <div className="text-xs text-gray-500 mt-0.5">Interest-based bank financing</div>
                    </button>
                    <button
                      type="button"
                      onClick={() => patchLoanForm({ banking_model: 'islamic' })}
                      className={`text-left rounded-lg border px-3 py-2 ${
                        loanForm.banking_model === 'islamic'
                          ? 'border-teal-500 bg-teal-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">Islamic banking</div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        Shariah structure · profit / markup wording
                      </div>
                    </button>
                  </div>
                </div>

                <label className="col-span-2">
                  <span className="text-gray-600">Product type</span>
                  <select
                    value={loanForm.product_type}
                    onChange={(e) => patchLoanForm({ product_type: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  >
                    {PRODUCT_OPTIONS.filter((p) =>
                      loanForm.banking_model === 'conventional'
                        ? !p.value.startsWith('islamic_')
                        : true,
                    ).map((p) => (
                      <option key={p.value} value={p.value}>
                        {p.label}
                      </option>
                    ))}
                  </select>
                </label>

                {loanForm.banking_model === 'islamic' && (
                  <label className="col-span-2">
                    <span className="text-gray-600">Islamic structure</span>
                    <select
                      value={loanForm.islamic_contract_variant}
                      onChange={(e) =>
                        patchLoanForm({ islamic_contract_variant: e.target.value })
                      }
                      className="mt-1 w-full border rounded-lg px-3 py-2"
                    >
                      {ISLAMIC_CONTRACTS.map((o) => (
                        <option key={o.value || 'none'} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                    <p className="mt-1 text-xs text-gray-500">
                      Same GL mechanics as conventional; label is for reporting clarity.
                    </p>
                  </label>
                )}

                {loanForm.product_type === 'islamic_facility' && (
                  <div className="col-span-2 text-sm text-sky-900 bg-sky-50 border border-sky-200 rounded-lg p-3">
                    Facility = overall Shariah limit. Disburse on <strong>Islamic deal</strong> rows
                    under this facility.
                  </div>
                )}

                {loanForm.product_type === 'islamic_deal' && (
                  <>
                    <label className="col-span-2">
                      <span className="text-gray-600">Parent Islamic facility</span>
                      <select
                        value={loanForm.parent_loan_id}
                        onChange={(e) => patchLoanForm({ parent_loan_id: e.target.value })}
                        className="mt-1 w-full border rounded-lg px-3 py-2"
                      >
                        <option value="">Select facility…</option>
                        {islamicFacilities.map((l) => (
                          <option key={l.id} value={l.id}>
                            {l.loan_no} — {formatMoney(l.sanction_amount)} limit
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="col-span-2">
                      <span className="text-gray-600">Deal reference (optional)</span>
                      <input
                        value={loanForm.deal_reference}
                        onChange={(e) => patchLoanForm({ deal_reference: e.target.value })}
                        className="mt-1 w-full border rounded-lg px-3 py-2"
                      />
                    </label>
                  </>
                )}

                <div className="col-span-2">
                  <span className="text-gray-600">Interest mode</span>
                  <div className="mt-1 grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => patchLoanForm({ interest_bearing: true })}
                      className={`text-left rounded-lg border px-3 py-2 ${
                        loanForm.interest_bearing
                          ? 'border-amber-500 bg-amber-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">
                        With {loanForm.banking_model === 'islamic' ? 'profit' : 'interest'}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        Rate, accrual, and split repayments
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => patchLoanForm({ interest_bearing: false })}
                      className={`text-left rounded-lg border px-3 py-2 ${
                        !loanForm.interest_bearing
                          ? 'border-gray-500 bg-gray-100'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">Without interest</div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        Principal-only · good for individual soft loans
                      </div>
                    </button>
                  </div>
                </div>

                <label className="col-span-2">
                  <span className="text-gray-600">Counterparty</span>
                  <select
                    value={loanForm.counterparty_id}
                    onChange={(e) => patchLoanForm({ counterparty_id: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  >
                    <option value="">Select…</option>
                    {counterparties
                      .filter((c) => c.is_active)
                      .map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.code} — {c.name} ({c.role_type})
                        </option>
                      ))}
                  </select>
                </label>
                <label>
                  <span className="text-gray-600">Loan no (optional)</span>
                  <input
                    value={loanForm.loan_no}
                    onChange={(e) => patchLoanForm({ loan_no: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                <label>
                  <span className="text-gray-600">Title</span>
                  <input
                    value={loanForm.title}
                    onChange={(e) => patchLoanForm({ title: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                <label>
                  <span className="text-gray-600">Sanction amount</span>
                  <input
                    type="number"
                    value={loanForm.sanction_amount}
                    onChange={(e) => patchLoanForm({ sanction_amount: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                {loanForm.interest_bearing ? (
                  <label>
                    <span className="text-gray-600">
                      Annual {loanForm.banking_model === 'islamic' ? 'profit' : 'interest'} %
                    </span>
                    <input
                      type="number"
                      value={loanForm.annual_interest_rate}
                      onChange={(e) => patchLoanForm({ annual_interest_rate: e.target.value })}
                      className="mt-1 w-full border rounded-lg px-3 py-2"
                    />
                  </label>
                ) : (
                  <div className="rounded-lg border border-dashed px-3 py-2 text-xs text-gray-500 flex items-center">
                    Rate locked at 0% (interest-free)
                  </div>
                )}
                <label>
                  <span className="text-gray-600">Term (months)</span>
                  <input
                    type="number"
                    value={loanForm.term_months}
                    onChange={(e) => patchLoanForm({ term_months: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                <label>
                  <span className="text-gray-600">Start date</span>
                  <input
                    type="date"
                    value={loanForm.start_date}
                    onChange={(e) => patchLoanForm({ start_date: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                {[
                  ['principal_account_id', 'Principal account'],
                  ['settlement_account_id', 'Settlement (cash/bank)'],
                  ...(loanForm.interest_bearing
                    ? ([
                        [
                          'interest_account_id',
                          loanForm.banking_model === 'islamic' ? 'Profit P&L' : 'Interest P&L',
                        ],
                        [
                          'interest_accrual_account_id',
                          loanForm.banking_model === 'islamic'
                            ? 'Profit accrual BS'
                            : 'Interest accrual BS',
                        ],
                      ] as const)
                    : []),
                ].map(([key, label]) => (
                  <label key={key} className="col-span-2">
                    <span className="text-gray-600">{label}</span>
                    <select
                      value={(loanForm as any)[key]}
                      onChange={(e) => patchLoanForm({ [key]: e.target.value } as any)}
                      className="mt-1 w-full border rounded-lg px-3 py-2"
                    >
                      <option value="">Select…</option>
                      {accounts.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.code} — {a.name}
                        </option>
                      ))}
                    </select>
                  </label>
                ))}
              </div>
              <div className="mt-5 flex justify-end gap-2">
                <button
                  onClick={() => setShowLoanForm(false)}
                  className="px-4 py-2 border rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  disabled={busy || !loanForm.counterparty_id}
                  onClick={createLoan}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm disabled:opacity-50"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        )}

        {showCpForm && (
          <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl w-full max-w-lg p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">New loan counterparty</h2>
                <button onClick={() => setShowCpForm(false)}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <label>
                  <span className="text-gray-600">Code</span>
                  <input
                    value={cpForm.code}
                    onChange={(e) => setCpForm({ ...cpForm, code: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                    placeholder="Auto if blank"
                  />
                </label>
                <label>
                  <span className="text-gray-600">Name</span>
                  <input
                    value={cpForm.name}
                    onChange={(e) => setCpForm({ ...cpForm, name: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  />
                </label>
                <label>
                  <span className="text-gray-600">Role</span>
                  <select
                    value={cpForm.role_type}
                    onChange={(e) => setCpForm({ ...cpForm, role_type: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  >
                    <option value="bank">Bank</option>
                    <option value="islamic_bank">Islamic bank</option>
                    <option value="nbfc">NBFC</option>
                    <option value="individual">Individual</option>
                    <option value="vendor">Vendor</option>
                    <option value="customer">Customer</option>
                    <option value="other">Other</option>
                  </select>
                </label>
                <label>
                  <span className="text-gray-600">Party kind</span>
                  <select
                    value={cpForm.party_kind}
                    onChange={(e) => setCpForm({ ...cpForm, party_kind: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  >
                    <option value="lender">Lender</option>
                    <option value="borrower">Borrower</option>
                    <option value="both">Both</option>
                    <option value="other">Other</option>
                  </select>
                </label>
                <label>
                  <span className="text-gray-600">Opening type</span>
                  <select
                    value={cpForm.opening_balance_type}
                    onChange={(e) =>
                      setCpForm({ ...cpForm, opening_balance_type: e.target.value })
                    }
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                  >
                    <option value="zero">Zero</option>
                    <option value="receivable">Receivable</option>
                    <option value="payable">Payable</option>
                  </select>
                </label>
                <label>
                  <span className="text-gray-600">Opening amount</span>
                  <input
                    type="number"
                    value={cpForm.opening_balance}
                    onChange={(e) => setCpForm({ ...cpForm, opening_balance: e.target.value })}
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                    disabled={cpForm.opening_balance_type === 'zero'}
                  />
                </label>
                <label className="col-span-2">
                  <span className="text-gray-600">As of (date)</span>
                  <input
                    type="date"
                    value={cpForm.opening_balance_as_of}
                    onChange={(e) =>
                      setCpForm({ ...cpForm, opening_balance_as_of: e.target.value })
                    }
                    className="mt-1 w-full border rounded-lg px-3 py-2"
                    disabled={cpForm.opening_balance_type === 'zero'}
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Journal date for the opening balance posting when type is receivable or payable.
                  </p>
                </label>
              </div>
              <div className="mt-5 flex justify-end gap-2">
                <button
                  onClick={() => setShowCpForm(false)}
                  className="px-4 py-2 border rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  disabled={busy || !cpForm.name}
                  onClick={createCounterparty}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm disabled:opacity-50"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
