'use client'

import { Suspense, useMemo } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import { REPORTS_CATALOG } from '@/lib/reports-catalog'
import { FileText } from 'lucide-react'

function ComingSoonInner() {
  const params = useSearchParams()
  const id = params.get('id') || ''
  const report = useMemo(() => REPORTS_CATALOG.find((r) => r.id === id), [id])

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-amber-100 rounded">
          <FileText className="h-6 w-6 text-amber-800" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {report?.title || 'Report coming soon'}
          </h1>
          <p className="text-sm text-gray-600 mt-0.5">
            Industry-standard report planned for this subscription pack.
          </p>
        </div>
      </div>
      <div className="bg-white border border-gray-300 rounded p-5 space-y-3 text-sm text-gray-700">
        {report ? (
          <>
            <p>{report.description}</p>
            <p>
              <span className="text-gray-500">Category:</span> {report.category}
              {report.industryGroup ? ` · ${report.industryGroup}` : ''}
            </p>
            <p className="text-amber-800 bg-amber-50 border border-amber-200 rounded px-3 py-2">
              This report is catalogued from OPERA / restaurant POS standards but is not live yet.
              Use related live reports from Report Center in the meantime.
            </p>
          </>
        ) : (
          <p>Unknown report id. Return to Report Center to browse available reports.</p>
        )}
        <Link href="/reports" className="inline-block text-slate-800 underline">
          ← Back to Report Center
        </Link>
      </div>
    </div>
  )
}

export default function ComingSoonReportPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <Suspense fallback={<div className="p-6 text-sm text-gray-600">Loading…</div>}>
            <ComingSoonInner />
          </Suspense>
        </main>
      </div>
    </ProtectedRoute>
  )
}
