'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'

export default function SaasBillingPage() {
  const [tenants, setTenants] = useState<any[]>([])
  const [savingId, setSavingId] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    const res = await apiClient.get('/superadmin/tenants')
    setTenants(res.data.tenants || [])
  }

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.detail || 'Failed to load billing data'))
  }, [])

  const renew = async (tenant: any, days: number) => {
    setSavingId(tenant.id)
    setMessage('')
    setError('')
    try {
      const base = tenant.subscription_expires_at
        ? new Date(tenant.subscription_expires_at)
        : new Date()
      if (base < new Date()) base.setTime(Date.now())
      base.setDate(base.getDate() + days)
      const iso = base.toISOString().slice(0, 10)
      await apiClient.patch(`/superadmin/tenants/${tenant.id}`, {
        subscription_expires_at: iso,
        is_active: true,
        subscription_plan: tenant.subscription_plan || 'standard',
      })
      setMessage(`Renewed ${tenant.name} for ${days} days (until ${iso})`)
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Renewal failed')
    } finally {
      setSavingId(null)
    }
  }

  const setPlan = async (tenant: any, plan: string) => {
    setSavingId(tenant.id)
    try {
      await apiClient.patch(`/superadmin/tenants/${tenant.id}`, { subscription_plan: plan })
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Plan update failed')
    } finally {
      setSavingId(null)
    }
  }

  const isExpired = (t: any) =>
    t.subscription_expires_at && new Date(t.subscription_expires_at) < new Date()

  return (
    <SaasLayout>
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Billing & subscriptions</h2>
          <p className="text-sm text-slate-600">
            Renew plans and enforce expiry for Hotel / Resort / Restaurant tenants.
          </p>
        </div>

        {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}
        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Tenant</th>
                <th className="px-4 py-3 font-medium">Plan</th>
                <th className="px-4 py-3 font-medium">Expires</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.id} className="border-t">
                  <td className="px-4 py-3">
                    <div className="font-medium">{t.name}</div>
                    <div className="text-xs capitalize text-slate-500">
                      {t.product_type} · {t.subdomain}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      className="rounded border px-2 py-1"
                      value={t.subscription_plan || 'standard'}
                      onChange={(e) => setPlan(t, e.target.value)}
                      disabled={savingId === t.id}
                    >
                      <option value="starter">Starter</option>
                      <option value="standard">Standard</option>
                      <option value="premium">Premium</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    {t.subscription_expires_at
                      ? new Date(t.subscription_expires_at).toLocaleDateString()
                      : 'No expiry'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${
                        isExpired(t)
                          ? 'bg-red-50 text-red-700'
                          : t.is_active
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {isExpired(t) ? 'Expired' : t.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => renew(t, 30)}
                        disabled={savingId === t.id}
                        className="rounded bg-indigo-600 px-2 py-1 text-xs text-white disabled:opacity-50"
                      >
                        +30 days
                      </button>
                      <button
                        onClick={() => renew(t, 365)}
                        disabled={savingId === t.id}
                        className="rounded border px-2 py-1 text-xs disabled:opacity-50"
                      >
                        +1 year
                      </button>
                      <Link href={`/saas/tenants/${t.id}`} className="text-xs text-indigo-600 hover:underline">
                        Configure
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
              {tenants.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No tenants yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </SaasLayout>
  )
}
