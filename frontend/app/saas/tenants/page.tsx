'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Pencil, Trash2 } from 'lucide-react'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'
import { PRODUCT_TYPES } from '@/lib/modules'

export default function SaasTenantsPage() {
  const [tenants, setTenants] = useState<any[]>([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError('')
      const params = filter !== 'all' ? `?product_type=${filter}` : ''
      const res = await apiClient.get(`/superadmin/tenants${params}`)
      setTenants(res.data.tenants || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tenants')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [filter])

  const removeTenant = async (tenant: any) => {
    const ok = window.confirm(
      `Delete tenant "${tenant.name}"? This cannot be undone.`
    )
    if (!ok) return
    setDeletingId(tenant.id)
    setError('')
    try {
      await apiClient.delete(`/superadmin/tenants/${tenant.id}`)
      setTenants((prev) => prev.filter((t) => t.id !== tenant.id))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete tenant')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <SaasLayout>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">Tenants</h2>
            <p className="text-sm text-slate-600">Hotels, resorts, and restaurants on the platform.</p>
          </div>
          <Link
            href="/saas/tenants/new"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            New Tenant
          </Link>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`rounded-full px-3 py-1 text-sm ${filter === 'all' ? 'bg-slate-900 text-white' : 'bg-white border'}`}
          >
            All
          </button>
          {PRODUCT_TYPES.map((p) => (
            <button
              key={p.key}
              onClick={() => setFilter(p.key)}
              className={`rounded-full px-3 py-1 text-sm capitalize ${
                filter === p.key ? 'bg-slate-900 text-white' : 'bg-white border'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          {loading ? (
            <div className="p-8 text-center text-slate-500">Loading...</div>
          ) : (
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Tenant</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Modules</th>
                  <th className="px-4 py-3 font-medium">Landing</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((t) => (
                  <tr key={t.id} className="border-t">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{t.name}</div>
                      <div className="text-xs text-slate-500">{t.subdomain} · {t.email}</div>
                    </td>
                    <td className="px-4 py-3 capitalize">{t.product_type}</td>
                    <td className="px-4 py-3 text-slate-600">{(t.enabled_modules || []).length}</td>
                    <td className="px-4 py-3">
                      {t.landing_enabled ? (
                        <Link href={`/site/${t.subdomain}`} className="text-indigo-600 hover:underline">
                          /site/{t.subdomain}
                        </Link>
                      ) : (
                        <span className="text-slate-400">Off</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          t.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {t.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <Link
                          href={`/saas/tenants/${t.id}`}
                          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-indigo-600"
                          title="Edit"
                        >
                          <Pencil className="h-4 w-4" />
                        </Link>
                        <button
                          type="button"
                          onClick={() => removeTenant(t)}
                          disabled={deletingId === t.id}
                          className="rounded-lg p-2 text-slate-600 hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {tenants.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-slate-500">
                      No tenants found for this filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </SaasLayout>
  )
}
