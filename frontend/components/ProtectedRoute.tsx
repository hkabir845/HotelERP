'use client'

import { useEffect, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import apiClient from '@/lib/api'
import {
  homePathForUser,
  moduleForAppPath,
  resolveRole,
  userHasModuleAccess,
} from '@/lib/rbac'

export default function ProtectedRoute({
  children,
  module,
  roles,
}: {
  children: React.ReactNode
  /** Optional explicit module requirement (overrides path inference). */
  module?: string | string[]
  /** Optional allowed roles (admin/superuser always pass). */
  roles?: string[]
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, user, access_token, hasHydrated, setAuth, setUser } = useAuthStore()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!hasHydrated) {
      const t = window.setTimeout(() => useAuthStore.setState({ hasHydrated: true }), 400)
      return () => window.clearTimeout(t)
    }

    const token = access_token || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null)

    const gateAccess = (u: NonNullable<typeof user>) => {
      const role = (u.role || '').toLowerCase()
      if (roles?.length) {
        const allowed = roles.map((r) => r.toLowerCase())
        if (
          !u.is_superuser &&
          role !== 'admin' &&
          !allowed.includes(role) &&
          !(role === 'fnb' && allowed.includes('restaurant')) &&
          !(role === 'manager' && allowed.includes('operations_manager'))
        ) {
          router.replace(`/access-denied?from=${encodeURIComponent(pathname || '')}`)
          return false
        }
      }

      const required =
        module ||
        moduleForAppPath(pathname || '')
      if (required) {
        const keys = Array.isArray(required) ? required : [required]
        const ok = keys.some((k) => userHasModuleAccess(u, k))
        if (!ok) {
          router.replace(`/access-denied?from=${encodeURIComponent(pathname || '')}`)
          return false
        }
      }
      return true
    }

    if (token && user && isAuthenticated) {
      if (gateAccess(user)) setReady(true)
      return
    }

    if (!token) {
      router.replace('/login')
      return
    }

    const verify = async () => {
      try {
        const me = await apiClient.get('/auth/me')
        const nextUser = me.data
        const refresh =
          (typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null) || ''
        if (useAuthStore.getState().access_token) {
          setAuth(
            nextUser,
            useAuthStore.getState().access_token!,
            useAuthStore.getState().refresh_token || refresh,
            nextUser.tenant_id || undefined,
            nextUser.tenant?.subdomain || undefined
          )
        } else {
          setUser(nextUser)
        }
        if (gateAccess(nextUser)) setReady(true)
      } catch {
        router.replace('/login')
      }
    }

    verify()
  }, [
    hasHydrated,
    access_token,
    user,
    isAuthenticated,
    router,
    pathname,
    module,
    roles,
    setAuth,
    setUser,
  ])

  if (!hasHydrated || !ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-700" />
      </div>
    )
  }

  return <>{children}</>
}

/** Helper for role dashboards — redirect if role is not allowed. */
export function useRoleDashboardGate(allowed: string[]) {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  useEffect(() => {
    if (!user) return
    if (user.is_superuser) return
    const role = resolveRole(user.role).key
    const ok =
      role === 'admin' ||
      allowed.includes(role) ||
      (role === 'fnb' && allowed.includes('restaurant')) ||
      (role === 'manager' && allowed.includes('operations_manager'))
    if (!ok) router.replace(homePathForUser(user))
  }, [user, router, allowed])
}
