'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import RoleDashboard from '@/components/RoleDashboard'
import { useAuthStore } from '@/lib/store'
import { homePathForUser, resolveRole } from '@/lib/rbac'

/** Admin / default landing — redirects specialized roles to their dashboard. */
export default function HomePage() {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)

  useEffect(() => {
    if (!user) return
    const path = homePathForUser(user)
    if (path !== '/home' && path !== '/saas') {
      router.replace(path)
    }
  }, [user, router])

  const role = resolveRole(user?.role).key
  if (role === 'admin' || role === 'staff' || !user) {
    return <RoleDashboard dash="admin" />
  }

  // Brief spinner while redirecting specialized roles
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-slate-700" />
      </div>
    </ProtectedRoute>
  )
}
