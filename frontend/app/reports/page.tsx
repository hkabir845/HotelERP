'use client'

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import { useAuthStore } from '@/lib/store'
import { PRODUCT_TYPES, type ProductType } from '@/lib/modules'
import {
  REPORT_CATEGORIES,
  filterReportsCatalog,
  reportsByCategory,
  type ReportStatus,
} from '@/lib/reports-catalog'
import { FileText, Search, Building2, UtensilsCrossed, Trees } from 'lucide-react'

export default function ReportsPage() {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  const productType = (user?.product_type || user?.tenant?.product_type || 'hotel') as ProductType
  const enabledModules = (user?.enabled_modules || user?.tenant?.enabled_modules || []) as string[]

  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string>('all')
  const [status, setStatus] = useState<ReportStatus | 'all'>('all')

  const filtered = useMemo(
    () =>
      filterReportsCatalog({
        productType,
        enabledModules,
        category,
        status,
        search,
      }),
    [productType, enabledModules, category, status, search],
  )

  const groups = useMemo(() => reportsByCategory(filtered), [filtered])
  const liveCount = filtered.filter((r) => r.status === 'live').length
  const plannedCount = filtered.filter((r) => r.status === 'planned').length
  const productLabel =
    PRODUCT_TYPES.find((p) => p.key === productType)?.label || productType
  const includesRooms = productType === 'hotel' || productType === 'resort' || productType === 'mixed'

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6 max-w-7xl">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-800 rounded">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Report Center</h1>
                  <p className="text-sm text-gray-600 mt-0.5">
                    Industry reports for your subscription — OPERA-style front office, F&amp;B POS,
                    accounts, inventory, and more.
                  </p>
                </div>
              </div>
              <div className="rounded border border-gray-300 bg-white px-4 py-2 text-sm">
                <div className="flex items-center gap-2 text-gray-800 font-medium">
                  {productType === 'restaurant' ? (
                    <UtensilsCrossed className="h-4 w-4" />
                  ) : productType === 'resort' ? (
                    <Trees className="h-4 w-4" />
                  ) : (
                    <Building2 className="h-4 w-4" />
                  )}
                  {productLabel}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {includesRooms
                    ? 'Rooms + in-built restaurant reports'
                    : 'Restaurant / F&B pack only (no frontdesk stay reports)'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {liveCount} live · {plannedCount} planned · {filtered.length} shown
                </p>
              </div>
            </div>

            <div className="mb-5 flex flex-wrap gap-3 items-center bg-white border border-gray-300 rounded p-3">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search reports…"
                  className="w-full border border-gray-300 rounded pl-8 pr-3 py-2 text-sm"
                />
              </div>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="all">All categories</option>
                {REPORT_CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as ReportStatus | 'all')}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="all">Live + planned</option>
                <option value="live">Live only</option>
                <option value="planned">Planned only</option>
              </select>
            </div>

            {groups.length === 0 ? (
              <div className="bg-white border border-gray-300 rounded p-8 text-center text-gray-600">
                No reports match this subscription and filters.
              </div>
            ) : (
              <div className="space-y-5">
                {groups.map((group) => (
                  <section
                    key={group.category}
                    className="bg-white border border-gray-300 rounded"
                  >
                    <div className="px-4 py-2.5 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
                      <h2 className="font-semibold text-gray-900">{group.category}</h2>
                      <span className="text-xs text-gray-500">{group.reports.length}</span>
                    </div>
                    <div className="divide-y divide-gray-100">
                      {group.reports.map((rep) => (
                        <button
                          key={rep.id}
                          type="button"
                          onClick={() => router.push(rep.path)}
                          className="w-full text-left px-4 py-3 hover:bg-slate-50 flex items-start justify-between gap-4"
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-medium text-gray-900">{rep.title}</span>
                              {rep.status === 'planned' && (
                                <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">
                                  Coming soon
                                </span>
                              )}
                              {rep.industryGroup && (
                                <span className="text-[10px] text-gray-400">{rep.industryGroup}</span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-0.5">{rep.description}</p>
                          </div>
                          <span className="text-xs text-gray-400 shrink-0 mt-1">Open →</span>
                        </button>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
