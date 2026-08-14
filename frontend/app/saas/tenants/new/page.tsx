'use client'

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'
import {
  MODULE_LABELS,
  MODULE_PRESETS,
  PRODUCT_TYPES,
  WEBSITE_TEMPLATES,
  defaultWebsiteTemplate,
  ModuleKey,
  ProductType,
  modulesForProduct,
} from '@/lib/modules'

export default function NewTenantPage() {
  const router = useRouter()
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    subdomain: '',
    domain: '',
    email: '',
    phone: '',
    product_type: 'hotel' as ProductType,
    subscription_plan: 'standard',
    subscription_expires_at: '',
    landing_enabled: true,
    landing_title: '',
    landing_tagline: '',
    landing_template: 'hotel',
    admin_email: '',
    admin_username: '',
    admin_password: 'Admin@123',
    enabled_modules: [...MODULE_PRESETS.hotel] as ModuleKey[],
  })

  const modules = useMemo(() => modulesForProduct(form.product_type), [form.product_type])

  const onProductChange = (product_type: ProductType) => {
    setForm((prev) => ({
      ...prev,
      product_type,
      enabled_modules: [...MODULE_PRESETS[product_type]],
      landing_template: defaultWebsiteTemplate(product_type, prev.subdomain),
    }))
  }

  const toggleModule = (key: ModuleKey) => {
    setForm((prev) => {
      const has = prev.enabled_modules.includes(key)
      let next = has
        ? prev.enabled_modules.filter((m) => m !== key)
        : [...prev.enabled_modules, key]
      if (key === 'recipes' && !has && !next.includes('fnb')) {
        next = [...next, 'fnb']
      }
      if (key === 'fnb' && has) {
        next = next.filter((m) => m !== 'recipes')
      }
      return { ...prev, enabled_modules: next }
    })
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = {
        ...form,
        subdomain: form.subdomain.trim().toLowerCase(),
        domain: form.domain.trim() || null,
        subscription_expires_at: form.subscription_expires_at || null,
        landing_title: form.landing_title || form.name,
        admin_email: form.admin_email || undefined,
        admin_username: form.admin_username || undefined,
      }
      const res = await apiClient.post('/superadmin/tenants', payload)
      router.push(`/saas/tenants/${res.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create tenant')
    } finally {
      setSaving(false)
    }
  }

  return (
    <SaasLayout>
      <form onSubmit={submit} className="mx-auto max-w-3xl space-y-6">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Create tenant website & ERP</h2>
          <p className="text-sm text-slate-600">
            Provision a hotel, resort, or restaurant. A professional public site is created and linked to the same
            rooms, rates, and kitchen menu used in the ERP.
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <section className="space-y-4 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Business details</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm sm:col-span-2">
              <span className="mb-1 block text-slate-600">Business name</span>
              <input
                required
                className="w-full rounded-lg border px-3 py-2"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Subdomain</span>
              <input
                required
                className="w-full rounded-lg border px-3 py-2"
                placeholder="turag"
                value={form.subdomain}
                onChange={(e) => setForm({ ...form, subdomain: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Custom domain (optional)</span>
              <input
                className="w-full rounded-lg border px-3 py-2"
                placeholder="www.example.com"
                value={form.domain}
                onChange={(e) => setForm({ ...form, domain: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Email</span>
              <input
                required
                type="email"
                className="w-full rounded-lg border px-3 py-2"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Product type</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={form.product_type}
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
              <span className="mb-1 block text-slate-600">Subscription plan</span>
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={form.subscription_plan}
                onChange={(e) => setForm({ ...form, subscription_plan: e.target.value })}
              >
                <option value="starter">Starter</option>
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-600">Expires (optional)</span>
              <input
                type="date"
                className="w-full rounded-lg border px-3 py-2"
                value={form.subscription_expires_at}
                onChange={(e) => setForm({ ...form, subscription_expires_at: e.target.value })}
              />
            </label>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-slate-900">Enabled modules</h3>
            <p className="text-xs text-slate-500">
              Hotel and resort include restaurant by default. Uncheck Food &amp; Beverage if they will not use the
              kitchen. Restaurant-only plans cannot enable rooms or housekeeping.
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            {modules.map((key) => (
              <label key={key} className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.enabled_modules.includes(key)}
                  onChange={() => toggleModule(key)}
                />
                {MODULE_LABELS[key]}
              </label>
            ))}
          </div>
        </section>

        <section className="space-y-4 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Public website</h3>
          <p className="text-xs text-slate-500">
            Guests book rooms and order food on the website; reservations and kitchen tickets appear in this tenant&apos;s
            ERP immediately.
          </p>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.landing_enabled}
              onChange={(e) => setForm({ ...form, landing_enabled: e.target.checked })}
            />
            Enable public website
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-600">Website style</span>
            <select
              className="w-full rounded-lg border px-3 py-2"
              value={form.landing_template}
              onChange={(e) => setForm({ ...form, landing_template: e.target.value })}
            >
              {WEBSITE_TEMPLATES.filter(
                (t) => t.product_types.includes(form.product_type) || form.product_type === 'mixed'
              ).map((t) => (
                <option key={t.key} value={t.key}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="Website title"
            value={form.landing_title}
            onChange={(e) => setForm({ ...form, landing_title: e.target.value })}
          />
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="Tagline shown on the homepage"
            value={form.landing_tagline}
            onChange={(e) => setForm({ ...form, landing_tagline: e.target.value })}
          />
        </section>

        <section className="space-y-4 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">Tenant admin (optional)</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <input
              className="rounded-lg border px-3 py-2 text-sm"
              placeholder="Admin email"
              value={form.admin_email}
              onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
            />
            <input
              className="rounded-lg border px-3 py-2 text-sm"
              placeholder="Admin username"
              value={form.admin_username}
              onChange={(e) => setForm({ ...form, admin_username: e.target.value })}
            />
            <input
              className="rounded-lg border px-3 py-2 text-sm sm:col-span-2"
              placeholder="Admin password"
              value={form.admin_password}
              onChange={(e) => setForm({ ...form, admin_password: e.target.value })}
            />
          </div>
        </section>

        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? 'Creating...' : 'Create website & workspace'}
        </button>
      </form>
    </SaasLayout>
  )
}
