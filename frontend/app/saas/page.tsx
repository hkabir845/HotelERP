'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import apiClient from '@/lib/api'
import SaasLayout from '@/components/SaasLayout'
import { Building2, Hotel, UtensilsCrossed, Palmtree, Users } from 'lucide-react'

interface Overview {
  tenants: { total: number; active: number }
  users: { total: number; active: number }
  revenue: { total: number }
  by_product_type?: Record<string, number>
}

export default function SaasDashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [tenants, setTenants] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const [dash, list] = await Promise.all([
          apiClient.get('/superadmin/dashboard'),
          apiClient.get('/superadmin/tenants'),
        ])
        setOverview(dash.data.overview)
        setTenants(list.data.tenants || [])
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load SaaS dashboard')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const cards = [
    {
      label: 'Tenants',
      value: overview?.tenants.total ?? 0,
      sub: `${overview?.tenants.active ?? 0} active`,
      icon: Building2,
    },
    {
      label: 'Users',
      value: overview?.users.total ?? 0,
      sub: `${overview?.users.active ?? 0} active`,
      icon: Users,
    },
    {
      label: 'Hotels',
      value: overview?.by_product_type?.hotel ?? 0,
      sub: 'product type',
      icon: Hotel,
    },
    {
      label: 'Restaurants',
      value: overview?.by_product_type?.restaurant ?? 0,
      sub: 'product type',
      icon: UtensilsCrossed,
    },
    {
      label: 'Resorts',
      value: overview?.by_product_type?.resort ?? 0,
      sub: 'product type',
      icon: Palmtree,
    },
  ]

  return (
    <SaasLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">SaaS Overview</h2>
            <p className="text-sm text-slate-600">
              Manage Hotel, Resort, and Restaurant tenants from one control panel.
            </p>
          </div>
          <Link
            href="/saas/billing"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Billing & renewals
          </Link>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-xl border bg-white p-8 text-center text-slate-500">Loading...</div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
              {cards.map((card) => {
                const Icon = card.icon
                return (
                  <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-slate-500">{card.label}</p>
                      <Icon className="h-4 w-4 text-indigo-500" />
                    </div>
                    <p className="mt-2 text-3xl font-semibold text-slate-900">{card.value}</p>
                    <p className="text-xs text-slate-500">{card.sub}</p>
                  </div>
                )
              })}
            </div>

            <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <h3 className="font-medium text-slate-900">Recent tenants</h3>
                <Link href="/saas/tenants" className="text-sm text-indigo-600 hover:underline">
                  View all
                </Link>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr>
                      <th className="px-4 py-2 font-medium">Name</th>
                      <th className="px-4 py-2 font-medium">Subdomain</th>
                      <th className="px-4 py-2 font-medium">Type</th>
                      <th className="px-4 py-2 font-medium">Plan</th>
                      <th className="px-4 py-2 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tenants.slice(0, 8).map((t) => (
                      <tr key={t.id} className="border-t">
                        <td className="px-4 py-2">
                          <Link href={`/saas/tenants/${t.id}`} className="font-medium text-indigo-700 hover:underline">
                            {t.name}
                          </Link>
                        </td>
                        <td className="px-4 py-2 text-slate-600">{t.subdomain}</td>
                        <td className="px-4 py-2 capitalize">{t.product_type}</td>
                        <td className="px-4 py-2 capitalize">{t.subscription_plan}</td>
                        <td className="px-4 py-2">
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs ${
                              t.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {t.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {tenants.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                          No tenants yet.{' '}
                          <Link href="/saas/tenants/new" className="text-indigo-600 hover:underline">
                            Create one
                          </Link>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </SaasLayout>
  )
}
