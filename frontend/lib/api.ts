import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

function isAuthHandshake(url?: string) {
  const path = url || ''
  return path.includes('/auth/login') || path.includes('/auth/refresh')
}

function onLoginPage() {
  return typeof window !== 'undefined' && window.location.pathname.startsWith('/login')
}

function clearSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  localStorage.removeItem('tenant_id')
  localStorage.removeItem('tenant_subdomain')
}

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Never attach a leftover session to the login request — a stale JWT
    // can make the backend reject the sign-in as 401 and bounce the page.
    if (isAuthHandshake(config.url)) {
      if (config.headers) {
        delete config.headers.Authorization
      }
      return config
    }

    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    const tenantId = localStorage.getItem('tenant_id')
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId
    }

    const tenantSubdomain = localStorage.getItem('tenant_subdomain')
    if (tenantSubdomain) {
      config.headers['X-Tenant-Subdomain'] = tenantSubdomain
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh and error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {}

    // Failed login/refresh must surface as a form error — not a page reload.
    if (isAuthHandshake(originalRequest.url)) {
      return Promise.reject(error)
    }

    // If token expired, try to refresh (once)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token: new_refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', new_refresh_token)

          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        clearSession()
        if (!onLoginPage()) {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }

      clearSession()
      if (!onLoginPage()) {
        window.location.href = '/login'
      }
    }

    // Subscription expired / payment required
    if (error.response?.status === 402) {
      const detail =
        error.response?.data?.detail ||
        'Subscription expired. Contact your platform administrator.'
      if (!onLoginPage()) {
        clearSession()
        window.location.href = `/login?error=${encodeURIComponent(detail)}`
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
