'use client'

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import { useAuthStore } from '@/lib/store'
import {
  buildAppsCatalog,
  categoryColor,
  filterAppsForUser,
  type AppTile,
} from '@/lib/apps-center'
import { homePathForUser } from '@/lib/rbac'
import {
  Search,
  LayoutGrid,
  ExternalLink,
  Star,
  ArrowLeft,
} from 'lucide-react'

const FAVORITES_KEY = 'hotelerp_apps_favorites'

function loadFavorites(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = localStorage.getItem(FAVORITES_KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

function saveFavorites(ids: string[]) {
  if (typeof window === 'undefined') return
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(ids))
}

function AppCard({
  app,
  favorite,
  onToggleFavorite,
  onOpen,
}: {
  app: AppTile
  favorite: boolean
  onToggleFavorite: () => void
  onOpen: () => void
}) {
  const color = categoryColor(app.category)
  return (
    <div className="group relative flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">
      <button
        type="button"
        onClick={onToggleFavorite}
        className="absolute right-2 top-2 rounded p-1 text-slate-300 hover:bg-slate-100 hover:text-amber-500"
        title={favorite ? 'Remove favorite' : 'Add favorite'}
        aria-label="Toggle favorite"
      >
        <Star className={`h-4 w-4 ${favorite ? 'fill-amber-400 text-amber-500' : ''}`} />
      </button>
      <button type="button" onClick={onOpen} className="flex flex-1 flex-col text-left">
        <span
          className="mb-3 flex h-11 w-11 items-center justify-center rounded-lg text-sm font-bold text-white shadow-sm"
          style={{ backgroundColor: color }}
        >
          {app.title
            .split(/\s+/)
            .slice(0, 2)
            .map((w) => w[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)}
        </span>
        <span className="pr-6 text-sm font-semibold text-slate-900 leading-snug">{app.title}</span>
        <span className="mt-1 text-[11px] font-medium uppercase tracking-wide" style={{ color }}>
          {app.category}
        </span>
        {app.breadcrumbs.length > 0 && (
          <span className="mt-1 line-clamp-2 text-[11px] text-slate-500">
            {app.breadcrumbs.join(' · ')}
          </span>
        )}
        <span className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-slate-600 opacity-0 transition group-hover:opacity-100">
          Open <ExternalLink className="h-3 w-3" />
        </span>
      </button>
    </div>
  )
}

export default function AppsCenterPage() {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string>('all')
  const [favorites, setFavorites] = useState<string[]>(() =>
    typeof window !== 'undefined' ? loadFavorites() : []
  )

  const allApps = useMemo(() => {
    const tenantName = user?.tenant?.name || 'Hotel'
    const catalog = buildAppsCatalog(tenantName, user)
    return filterAppsForUser(catalog, {
      enabledModules: user?.enabled_modules,
      role: user?.role,
      isSuperuser: !!user?.is_superuser,
    })
  }, [user])

  const categories = useMemo(() => {
    const set = new Set(allApps.map((a) => a.category))
    return ['all', ...Array.from(set)]
  }, [allApps])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return allApps.filter((app) => {
      if (category !== 'all' && app.category !== category) return false
      if (!q) return true
      return app.keywords.includes(q) || app.title.toLowerCase().includes(q)
    })
  }, [allApps, query, category])

  const favoriteApps = useMemo(
    () => filtered.filter((a) => favorites.includes(a.id)),
    [filtered, favorites]
  )

  const grouped = useMemo(() => {
    const map = new Map<string, AppTile[]>()
    for (const app of filtered) {
      if (!map.has(app.category)) map.set(app.category, [])
      map.get(app.category)!.push(app)
    }
    return Array.from(map.entries())
  }, [filtered])

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => {
      const next = prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
      saveFavorites(next)
      return next
    })
  }

  const dash = homePathForUser(user)

  return (
    <ProtectedRoute>
      <div className="flex h-screen" style={{ background: '#f0f2f5' }}>
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto">
          <div className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-6 py-4 backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => router.push(dash)}
                  className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-50"
                  title="Back to dashboard"
                >
                  <ArrowLeft className="h-4 w-4" />
                </button>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 text-white">
                  <LayoutGrid className="h-5 w-5" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900">Apps Center</h1>
                  <p className="text-sm text-slate-600">
                    {filtered.length} apps available for{' '}
                    <span className="font-medium">{user?.role_label || user?.role || 'your role'}</span>
                  </p>
                </div>
              </div>
              <div className="relative w-full max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search apps, screens, reports…"
                  className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
                />
              </div>
            </div>
            <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
              {categories.map((cat) => {
                const active = category === cat
                const color = cat === 'all' ? '#0f172a' : categoryColor(cat)
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setCategory(cat)}
                    className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                      active ? 'text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                    style={active ? { backgroundColor: color } : undefined}
                  >
                    {cat === 'all' ? 'All apps' : cat}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="p-6 space-y-8">
            {favoriteApps.length > 0 && (
              <section>
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                  <Star className="h-4 w-4 fill-amber-400 text-amber-500" /> Favorites
                </h2>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                  {favoriteApps.map((app) => (
                    <AppCard
                      key={`fav-${app.id}`}
                      app={app}
                      favorite
                      onToggleFavorite={() => toggleFavorite(app.id)}
                      onOpen={() => router.push(app.path)}
                    />
                  ))}
                </div>
              </section>
            )}

            {filtered.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
                <LayoutGrid className="mx-auto mb-3 h-10 w-10 text-slate-300" />
                <p className="font-medium text-slate-800">No apps match your search</p>
                <p className="mt-1 text-sm text-slate-500">Try another keyword or clear the category filter.</p>
              </div>
            ) : (
              grouped.map(([cat, apps]) => (
                <section key={cat}>
                  <div className="mb-3 flex items-center gap-2">
                    <span
                      className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: categoryColor(cat) }}
                    />
                    <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
                      {cat}
                    </h2>
                    <span className="text-xs text-slate-400">({apps.length})</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                    {apps.map((app) => (
                      <AppCard
                        key={app.id}
                        app={app}
                        favorite={favorites.includes(app.id)}
                        onToggleFavorite={() => toggleFavorite(app.id)}
                        onOpen={() => router.push(app.path)}
                      />
                    ))}
                  </div>
                </section>
              ))
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
