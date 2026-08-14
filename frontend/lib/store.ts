import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ProductType } from './modules'

export interface TenantInfo {
  id: number
  name: string
  subdomain: string
  product_type: ProductType | string
  enabled_modules: string[]
  landing_enabled?: boolean
  is_active?: boolean
  subscription_plan?: string
  logo?: string | null
}

export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  phone?: string
  role: string
  role_label?: string
  home_path?: string
  capabilities?: string[]
  rbac?: {
    role?: string
    role_label?: string
    home_path?: string
    modules?: string[]
    capabilities?: string[]
    color?: string
  }
  tenant_id?: number
  is_active: boolean
  is_superuser: boolean
  is_staff: boolean
  avatar?: string
  department?: string
  designation?: string
  product_type?: string
  enabled_modules?: string[]
  tenant?: TenantInfo | null
}

interface AuthState {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  tenant_id: number | null
  tenant_subdomain: string | null
  isAuthenticated: boolean
  hasHydrated: boolean
  setAuth: (
    user: User,
    access_token: string,
    refresh_token: string,
    tenant_id?: number,
    tenant_subdomain?: string
  ) => void
  setUser: (user: User | null) => void
  logout: () => void
  setHasHydrated: (value: boolean) => void
}

function syncTokenKeys(
  access_token?: string | null,
  refresh_token?: string | null,
  tenant_id?: number | null,
  tenant_subdomain?: string | null
) {
  if (typeof window === 'undefined') return
  if (access_token) localStorage.setItem('access_token', access_token)
  else localStorage.removeItem('access_token')
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token)
  else localStorage.removeItem('refresh_token')
  if (tenant_id) localStorage.setItem('tenant_id', tenant_id.toString())
  else localStorage.removeItem('tenant_id')
  if (tenant_subdomain) localStorage.setItem('tenant_subdomain', tenant_subdomain)
  else localStorage.removeItem('tenant_subdomain')
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      tenant_id: null,
      tenant_subdomain: null,
      isAuthenticated: false,
      hasHydrated: false,
      setAuth: (user, access_token, refresh_token, tenant_id, tenant_subdomain) => {
        syncTokenKeys(access_token, refresh_token, tenant_id || null, tenant_subdomain || null)
        set({
          user,
          access_token,
          refresh_token,
          tenant_id: tenant_id || null,
          tenant_subdomain: tenant_subdomain || null,
          isAuthenticated: true,
        })
      },
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => {
        syncTokenKeys(null, null, null, null)
        localStorage.removeItem('user')
        set({
          user: null,
          access_token: null,
          refresh_token: null,
          tenant_id: null,
          tenant_subdomain: null,
          isAuthenticated: false,
        })
      },
      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        access_token: state.access_token,
        refresh_token: state.refresh_token,
        tenant_id: state.tenant_id,
        tenant_subdomain: state.tenant_subdomain,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state, error) => {
        if (typeof window === 'undefined') return
        if (error) {
          useAuthStore.setState({ hasHydrated: true })
          return
        }
        const token = state?.access_token || localStorage.getItem('access_token')
        const refresh = state?.refresh_token || localStorage.getItem('refresh_token')
        const user = state?.user
        if (token && user) {
          syncTokenKeys(token, refresh, state?.tenant_id, state?.tenant_subdomain)
          useAuthStore.setState({
            access_token: token,
            refresh_token: refresh,
            isAuthenticated: true,
            hasHydrated: true,
          })
        } else {
          useAuthStore.setState({ hasHydrated: true })
        }
      },
    }
  )
)

function markHydrated() {
  if (!useAuthStore.getState().hasHydrated) {
    useAuthStore.setState({ hasHydrated: true })
  }
}

if (typeof window !== 'undefined') {
  useAuthStore.persist.onFinishHydration(markHydrated)
  queueMicrotask(markHydrated)
  window.setTimeout(markHydrated, 250)
}
