'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  Building2,
  CreditCard,
  LayoutDashboard,
  LogOut,
  PlusCircle,
  Settings2,
  Users,
} from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import ProtectedRoute from '@/components/ProtectedRoute'

export default function SaasLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const nav = [
    { href: '/saas', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/saas/tenants', label: 'Tenants', icon: Building2 },
    { href: '/saas/tenants/new', label: 'New Tenant', icon: PlusCircle },
    { href: '/saas/billing', label: 'Billing', icon: CreditCard },
  ]

  if (user && !user.is_superuser) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
          <div className="max-w-md rounded-xl border bg-white p-8 text-center shadow-sm">
            <Settings2 className="mx-auto mb-3 h-10 w-10 text-slate-400" />
            <h1 className="text-xl font-semibold text-slate-900">SaaS Control Panel</h1>
            <p className="mt-2 text-sm text-slate-600">
              Only platform superadmins can access this area.
            </p>
            <button
              onClick={() => router.push('/home')}
              className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
            >
              Go to ERP
            </button>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-100">
        <header className="border-b border-slate-200 bg-slate-950 text-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400">Platform</p>
              <h1 className="text-lg font-semibold">Hospitality SaaS Control Panel</h1>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <span className="hidden sm:inline text-slate-300">
                <Users className="mr-1 inline h-4 w-4" />
                {user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-3 py-1.5 hover:bg-slate-700"
              >
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[220px_1fr]">
          <aside className="h-fit rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <nav className="space-y-1">
              {nav.map((item) => {
                const active = pathname === item.href
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
                      active
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                )
              })}
              <Link
                href="/home"
                className="mt-4 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-50"
              >
                Open sample ERP home
              </Link>
            </nav>
          </aside>
          <main>{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
