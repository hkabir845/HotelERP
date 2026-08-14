'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'
import LandingContentEditor from '@/components/saas/LandingContentEditor'
import { DEFAULT_TURAG_CONTENT, mergeLandingContent } from '@/lib/landings/turag-content'
import { WEBSITE_TEMPLATES } from '@/lib/modules'

export default function TenantWebsiteEditorPage() {
  const params = useParams()
  const router = useRouter()
  const tenantId = params.id as string
  const [tenant, setTenant] = useState<any>(null)
  const [content, setContent] = useState<any>(DEFAULT_TURAG_CONTENT)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get(`/superadmin/tenants/${tenantId}`)
        setTenant(res.data)
        setContent(mergeLandingContent(res.data.landing_content))
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load tenant website')
      }
    }
    load()
  }, [tenantId])

  const save = async () => {
    if (!tenant) return
    setSaving(true)
    setMessage('')
    setError('')
    try {
      const res = await apiClient.patch(`/superadmin/tenants/${tenantId}`, {
        landing_enabled: tenant.landing_enabled,
        landing_title: tenant.landing_title,
        landing_tagline: tenant.landing_tagline,
        landing_template: tenant.landing_template,
        seo_title: tenant.seo_title,
        seo_description: tenant.seo_description,
        seo_keywords: tenant.seo_keywords,
        og_image: tenant.og_image,
        logo: tenant.logo,
        landing_content: content,
      })
      setTenant(res.data)
      setContent(mergeLandingContent(res.data.landing_content))
      setMessage('Website content saved. Public site will refresh within 30 seconds.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
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
        <div className="rounded-xl border bg-white p-8 text-center text-slate-500">Loading website editor...</div>
      </SaasLayout>
    )
  }

  return (
    <SaasLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <button onClick={() => router.push(`/saas/tenants/${tenantId}`)} className="text-sm text-indigo-600 hover:underline">
              ← Back to tenant
            </button>
            <h2 className="mt-1 text-2xl font-semibold text-slate-900">Website editor</h2>
            <p className="text-sm text-slate-600">
              Public site for {tenant.name}. Rooms, rates, and the kitchen menu always come from the ERP — edit copy
              and SEO here.
              {tenant.landing_enabled && (
                <>
                  {' '}
                  ·{' '}
                  <Link href={`/site/${tenant.subdomain}`} className="text-indigo-600 hover:underline" target="_blank">
                    View live
                  </Link>
                </>
              )}
            </p>
          </div>
          <button
            type="button"
            onClick={save}
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save website'}
          </button>
        </div>

        {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}
        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-medium text-slate-900">SEO & indexing</h3>
          <p className="text-xs text-slate-500">Search title, description, keywords, and social share image.</p>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={!!tenant.landing_enabled}
              onChange={(e) => setTenant({ ...tenant, landing_enabled: e.target.checked })}
            />
            Public landing enabled
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-600">Website template</span>
            <select
              className="w-full rounded-lg border px-3 py-2"
              value={tenant.landing_template || 'hotel'}
              onChange={(e) => setTenant({ ...tenant, landing_template: e.target.value })}
            >
              {WEBSITE_TEMPLATES.map((t) => (
                <option key={t.key} value={t.key}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <div className="rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-indigo-900">
            Guest booking writes to Front Desk reservations. Food orders write to F&amp;B with serve time at a restaurant
            table or guest room. Change rooms/menus in the tenant ERP — the website updates automatically.
          </div>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.seo_title || ''}
            onChange={(e) => setTenant({ ...tenant, seo_title: e.target.value })}
            placeholder="SEO title"
          />
          <textarea
            className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.seo_description || ''}
            onChange={(e) => setTenant({ ...tenant, seo_description: e.target.value })}
            placeholder="SEO description"
          />
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.seo_keywords || ''}
            onChange={(e) => setTenant({ ...tenant, seo_keywords: e.target.value })}
            placeholder="Keywords, comma separated"
          />
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.og_image || ''}
            onChange={(e) => setTenant({ ...tenant, og_image: e.target.value })}
            placeholder="Open Graph image URL or /path"
          />
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm"
            value={tenant.logo || ''}
            onChange={(e) => setTenant({ ...tenant, logo: e.target.value })}
            placeholder="Logo URL or /path"
          />
        </section>

        <section className="space-y-4 rounded-xl border bg-white p-5 shadow-sm">
          <div>
            <h3 className="font-medium text-slate-900">Page copy & media</h3>
            <p className="text-xs text-slate-500">
              Edit every visible character, button label, image path, and gallery caption. Changes publish to the live
              guest site.
            </p>
          </div>
          <LandingContentEditor value={content} onChange={setContent} />
        </section>
      </div>
    </SaasLayout>
  )
}
