'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import apiClient from '@/lib/api'
import { Eye, EyeOff } from 'lucide-react'
import TuragLogo from '@/components/landings/TuragLogo'
import { DEMO_ROLE_LOGINS, homePathForUser } from '@/lib/rbac'

export default function LoginPage() {
  const router = useRouter()
  const { isAuthenticated, setAuth, user, access_token, hasHydrated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    tenant_subdomain: 'turag',
  })

  const [siteSlug, setSiteSlug] = useState('turag')

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const qErr = params.get('error')
      if (qErr) setError(qErr)
      const from = (params.get('site') || params.get('from') || '').trim().toLowerCase()
      if (from) setSiteSlug(from)
    }
  }, [])

  useEffect(() => {
    if (!hasHydrated) return
    if (isAuthenticated && user && access_token) {
      router.replace(homePathForUser(user))
    }
  }, [hasHydrated, isAuthenticated, user, access_token, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        username: formData.username.trim(),
        password: formData.password,
        ...(formData.tenant_subdomain.trim()
          ? { tenant_subdomain: formData.tenant_subdomain.trim() }
          : {}),
      }

      const response = await apiClient.post('/auth/login', payload)
      const { access_token: accessToken, refresh_token } = response.data

      const userResponse = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })

      const nextUser = userResponse.data

      setAuth(
        nextUser,
        accessToken,
        refresh_token,
        nextUser.tenant_id || undefined,
        payload.tenant_subdomain || nextUser.tenant?.subdomain || undefined
      )

      router.replace(homePathForUser(nextUser))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (email: string) => {
    setFormData((prev) => ({
      ...prev,
      username: email,
      password: 'Admin@123',
      tenant_subdomain: email.includes('superadmin') ? '' : prev.tenant_subdomain || 'turag',
    }))
  }

  const isTuragLogin = formData.tenant_subdomain.trim().toLowerCase() === 'turag'
  const websiteHref = `/site/${(formData.tenant_subdomain.trim() || siteSlug || 'turag').toLowerCase()}`
  const demos = DEMO_ROLE_LOGINS()

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200 px-4 py-10">
      <div className="absolute left-4 top-4 z-10 sm:left-6 sm:top-6">
        <TuragLogo href={websiteHref} heightClass="h-12 sm:h-16" />
      </div>
      <div className="w-full max-w-5xl grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-8 p-8 sm:p-10 bg-white rounded-xl shadow-lg">
          <div className="flex min-h-[5rem] flex-col items-center justify-center">
            {isTuragLogin ? (
              <>
                <TuragLogo heightClass="h-16" />
                <p className="mt-3 text-center text-sm text-[#5d6f68]">Role-based staff sign in</p>
              </>
            ) : (
              <>
                <h2 className="text-center text-3xl font-extrabold text-gray-900">Hotel ERP</h2>
                <p className="mt-2 text-center text-sm text-gray-600">Sign in to your account</p>
              </>
            )}
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-800">{error}</div>
              </div>
            )}

            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <label htmlFor="username" className="sr-only">
                  Username or Email
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Username or Email"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />
              </div>
              <div className="relative">
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              <div>
                <label htmlFor="tenant_subdomain" className="sr-only">
                  Tenant Subdomain (Optional)
                </label>
                <input
                  id="tenant_subdomain"
                  name="tenant_subdomain"
                  type="text"
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Tenant Subdomain (e.g., turag) - Optional"
                  value={formData.tenant_subdomain}
                  onChange={(e) => setFormData({ ...formData, tenant_subdomain: e.target.value })}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-slate-800 hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-slate-900">Try a hotel role</h3>
          <p className="mt-1 text-sm text-slate-600">
            Each role opens a tailored dashboard and menu (password{' '}
            <code className="rounded bg-slate-100 px-1">Admin@123</code>).
          </p>
          <div className="mt-4 space-y-2">
            {demos.map((role) => (
              <button
                key={role.key}
                type="button"
                onClick={() => fillDemo(role.demoEmail!)}
                className="flex w-full items-start gap-3 rounded-lg border border-slate-200 px-3 py-2.5 text-left transition hover:border-slate-400 hover:bg-slate-50"
              >
                <span
                  className="mt-0.5 inline-block h-3 w-3 shrink-0 rounded-full"
                  style={{ backgroundColor: role.color }}
                />
                <span>
                  <span className="block text-sm font-semibold text-slate-900">{role.label}</span>
                  <span className="block text-xs text-slate-500">{role.demoEmail}</span>
                </span>
              </button>
            ))}
            <button
              type="button"
              onClick={() => {
                setFormData({
                  username: 'superadmin@admin.com',
                  password: 'Admin@123',
                  tenant_subdomain: '',
                })
              }}
              className="flex w-full items-start gap-3 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2.5 text-left"
            >
              <span className="mt-0.5 inline-block h-3 w-3 shrink-0 rounded-full bg-indigo-500" />
              <span>
                <span className="block text-sm font-semibold text-indigo-900">Platform Superadmin</span>
                <span className="block text-xs text-indigo-700">
                  superadmin@admin.com · leave subdomain blank
                </span>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
