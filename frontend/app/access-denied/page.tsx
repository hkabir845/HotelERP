'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { ShieldOff } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { homePathForUser, resolveRole } from '@/lib/rbac'

function AccessDeniedInner() {
  const params = useSearchParams()
  const from = params.get('from') || ''
  const user = useAuthStore((s) => s.user)
  const home = homePathForUser(user)
  const role = resolveRole(user?.role)

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 text-rose-600">
          <ShieldOff className="h-7 w-7" />
        </div>
        <h1 className="text-xl font-bold text-slate-900">Access denied</h1>
        <p className="mt-2 text-sm text-slate-600">
          Your role <span className="font-semibold">{role.label}</span> does not include this area.
          {from ? (
            <>
              {' '}
              (<code className="rounded bg-slate-100 px-1 text-xs">{from}</code>)
            </>
          ) : null}
        </p>
        <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
          <Link
            href={home}
            className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900"
          >
            Go to my dashboard
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Switch user
          </Link>
        </div>
      </div>
    </div>
  )
}

export default function AccessDeniedPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-slate-700" />
        </div>
      }
    >
      <AccessDeniedInner />
    </Suspense>
  )
}
