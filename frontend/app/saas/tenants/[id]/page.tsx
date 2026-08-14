'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'
import {
  MODULE_LABELS,
  MODULE_PRESETS,
  PRODUCT_TYPES,
  ModuleKey,
  ProductType,
  modulesForProduct,
} from '@/lib/modules'

export default function TenantDetailPage() {
  const params = useParams()
  const router = useRouter()
  const tenantId = params.id as string
  const [tenant, setTenant] = useState<any>(null)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [adminUsername, setAdminUsername] = useState('')
  const [adminEmail, setAdminEmail] = useState('')
  const [adminPassword, setAdminPassword] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get(`/superadmin/tenants/${tenantId}`)
        setTenant(res.data)
        setAdminUsername(res.data.admin?.username || '')
        setAdminEmail(res.data.admin?.email || res.data.email || '')
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load tenant')
      }
    }
    load()
  }, [tenantId])

  const onProductChange = (product_type: ProductType) => {
    setTenant((prev: any) => ({
      ...prev,
      product_type,
      enabled_modules: [...MODULE_PRESETS[product_type]],
    }))
  }

  const toggleModule = (key: ModuleKey) => {
    setTenant((prev: any) => {
      const mods: string[] = prev.enabled_modules || []
      const has = mods.includes(key)
      let next = has ? mods.filter((m) => m !== key) : [...mods, key]
      if (key === 'recipes' && !has && !next.includes('fnb')) next = [...next, 'fnb']
      if (key === 'fnb' && has) next = next.filter((m) => m !== 'recipes')
      return { ...prev, enabled_modules: next }
    })
  }

  const save = async () => {
    if (!tenant) return
    setSaving(true)
    setMessage('')
    setError('')
    try {
      await apiClient.patch(`/superadmin/tenants/${tenantId}`, {
        name: tenant.name,
        email: tenant.email,
        phone: tenant.phone,
        domain: tenant.domain || null,
        is_active: tenant.is_active,
        subscription_plan: tenant.subscription_plan,
        subscription_expires_at: tenant.subscription_expires_at
          ? String(tenant.subscription_expires_at).slice(0, 10)
          : null,
        product_type: tenant.product_type,
        enabled_modules: tenant.enabled_modules,
        landing_enabled: tenant.landing_enabled,
        landing_title: tenant.landing_title,
        landing_tagline: tenant.landing_tagline,
        landing_template: tenant.landing_template,
        currency: tenant.currency || 'BDT',
        timezone: tenant.timezone || 'Asia/Dhaka',
        date_format: tenant.date_format || 'DD/MM/YYYY',
        time_format: tenant.time_format || '12h',
        admin_username: adminUsername.trim() || undefined,
        admin_email: adminEmail.trim() || undefined,
        admin_password: adminPassword.trim() || undefined,
      })
      router.push('/saas/tenants')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
      setSaving(false)
    }
  }

  if (error && !tenant) {
    return (
      <SaasLayout>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
      </SaasLayout>
    )
  }

  if (!tenant) {
    return (
      <SaasLayout>
        <div className="rounded-xl border bg-white p-8 text-center text-slate-500">Loading...</div>
      </SaasLayout>
    )
  }

  return (
    <SaasLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <button onClick={() => router.push('/saas/tenants')} className="text-sm text-indigo-600 hover:underline">
              ← Back to tenants
            </button>
            <h2 className="mt-1 text-2xl font-semibold text-slate-900">{tenant.name}</h2>
            <p className="text-sm text-slate-600">
              subdomain: <code>{tenant.subdomain}</code>
              {tenant.landing_enabled && (
                <>
                  {' '}
                  ·{' '}
                  <Link href={`/site/${tenant.subdomain}`} className="text-indigo-600 hover:underline">
                    Public landing
                  </Link>
                  {' · '}
                  <Link href={`/saas/tenants/${tenant.id}/website`} className="text-indigo-600 hover:underline">
                    Edit website
                  </Link>
                </>
              )}
            </p>
          </div>
          <button
            onClick={save}
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save changes'}
          </button>
        </div>

        {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}
        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="grid gap-4 rounded-xl border bg-white p-5 shadow-sm sm:grid-cols-2">
          <label className="text-sm sm:col-span-2">
            <span className="mb-1 block text-slate-600">Name</span>
            <input
              className="w-full rounded-lg border px-3 py-2"
              value={tenant.name || ''}
              onChange={(e) => setTenant({ ...tenant, name: e.target.value })}
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Product type</span>
            <select
              className="w-full rounded-lg border px-3 py-2"
              value={tenant.product_type}
              onChange={(e) => onProductChange(e.target.value as ProductType)}
            >
              {PRODUCT_TYPES.map((p) => (
                <option key={p.key} value={p.key}>
                  {p.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Plan</span>
            <select
              className="w-full rounded-lg border px-3 py-2"
              value={tenant.subscription_plan || 'standard'}
              onChange={(e) => setTenant({ ...tenant, subscription_plan: e.target.value })}
            >
              <option value="starter">Starter</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Subscription expires</span>
            <input
              type="date"
              className="w-full rounded-lg border px-3 py-2"
              value={
                tenant.subscription_expires_at
                  ? String(tenant.subscription_expires_at).slice(0, 10)
                  : ''
              }
              onChange={(e) =>
                setTenant({ ...tenant, subscription_expires_at: e.target.value || null })
              }
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Custom domain</span>
            <input
              className="w-full rounded-lg border px-3 py-2"
              value={tenant.domain || ''}
              onChange={(e) => setTenant({ ...tenant, domain: e.target.value })}
              placeholder="e.g. www.turagresort.com"
            />
          </label>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input
              type="checkbox"
              checked={!!tenant.is_active}
              onChange={(e) => setTenant({ ...tenant, is_active: e.target.checked })}
            />
            Tenant active
          </label>
          <p className="text-xs text-slate-500 sm:col-span-2">
            Point the custom domain DNS to this app. Guests hitting that host are routed to the
            public landing (see{' '}
            <Link href="/saas/billing" className="text-indigo-600 hover:underline">
              Billing
            </Link>{' '}
            for renewals).
          </p>
        </section>

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Admin login</h3>
          <p className="text-xs text-slate-500">
            Username and password for this company&apos;s ERP. Leave password blank to keep the current one.
          </p>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Username</span>
              <input
                className="w-full rounded-lg border px-3 py-2"
                value={adminUsername}
                onChange={(e) => setAdminUsername(e.target.value)}
                autoComplete="off"
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Email</span>
              <input
                type="email"
                className="w-full rounded-lg border px-3 py-2"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                autoComplete="off"
              />
            </label>
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Password</span>
              <input
                type="password"
                className="w-full rounded-lg border px-3 py-2"
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                placeholder={tenant.admin ? 'Leave blank to keep current password' : 'Set a password'}
                autoComplete="new-password"
              />
            </label>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Currency, date &amp; time</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Currency</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={tenant.currency || 'BDT'}
                onChange={(e) => setTenant({ ...tenant, currency: e.target.value })}
              >
                <option value="BDT">BDT — Bangladeshi Taka</option>
                <option value="USD">USD — US Dollar</option>
                <option value="EUR">EUR — Euro</option>
                <option value="GBP">GBP — British Pound</option>
                <option value="INR">INR — Indian Rupee</option>
                <option value="AED">AED — UAE Dirham</option>
                <option value="SAR">SAR — Saudi Riyal</option>
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Timezone</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={tenant.timezone || 'Asia/Dhaka'}
                onChange={(e) => setTenant({ ...tenant, timezone: e.target.value })}
              >
                <option value="Asia/Dhaka">Asia/Dhaka (GMT+6)</option>
                <option value="Asia/Kolkata">Asia/Kolkata (GMT+5:30)</option>
                <option value="Asia/Dubai">Asia/Dubai (GMT+4)</option>
                <option value="UTC">UTC</option>
                <option value="Europe/London">Europe/London</option>
                <option value="America/New_York">America/New_York</option>
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Date format</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={tenant.date_format || 'DD/MM/YYYY'}
                onChange={(e) => setTenant({ ...tenant, date_format: e.target.value })}
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                <option value="DD-MM-YYYY">DD-MM-YYYY</option>
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Time format</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={tenant.time_format || '12h'}
                onChange={(e) => setTenant({ ...tenant, time_format: e.target.value })}
              >
                <option value="12h">12-hour (3:45 PM)</option>
                <option value="24h">24-hour (15:45)</option>
              </select>
            </label>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Modules</h3>
          <p className="text-xs text-slate-500">
            Hotel and resort always include a restaurant. Uncheck Food &amp; Beverage if that property will not use
            dining. Restaurant-only subscriptions show restaurant modules only — no rooms or housekeeping.
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {modulesForProduct(tenant.product_type).map((key) => (
              <label key={key} className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm">
                <input
                  type="checkbox"
                  checked={(tenant.enabled_modules || []).includes(key)}
                  onChange={() => toggleModule(key)}
                />
                {MODULE_LABELS[key]}
              </label>
            ))}
          </div>
        </section>

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Landing page</h3>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={!!tenant.landing_enabled}
              onChange={(e) => setTenant({ ...tenant, landing_enabled: e.target.checked })}
            />
            Enable public landing page
          </label>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.landing_title || ''}
            onChange={(e) => setTenant({ ...tenant, landing_title: e.target.value })}
            placeholder="Landing title"
          />
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.landing_tagline || ''}
            onChange={(e) => setTenant({ ...tenant, landing_tagline: e.target.value })}
            placeholder="Tagline"
          />
          <p className="text-xs text-slate-500">
            For full character-level copy, SEO, gallery, and images use the{' '}
            <Link href={`/saas/tenants/${tenant.id}/website`} className="text-indigo-600 hover:underline">
              website editor
            </Link>
            .
          </p>
        </section>
      </div>
    </SaasLayout>
  )
}
