/**
 * Apps Center catalog — flattens GYOROOM menubar into launchable apps.
 */
import type { ModuleKey } from './modules'
import { SIDEBAR_MODULE_MAP } from './modules'
import { getGyoroomMenu, type MenuItem } from './gyoroom-menu'
import { homePathForUser, roleAllowsMenuSection } from './rbac'

export type AppTile = {
  id: string
  title: string
  path: string
  category: string
  module: ModuleKey | null
  breadcrumbs: string[]
  keywords: string
}

function walk(
  items: MenuItem[],
  category: string,
  module: ModuleKey | null,
  trail: string[],
  out: AppTile[]
) {
  for (const item of items) {
    const nextTrail = [...trail, item.title]
    const mod = item.module || module
    if (item.path) {
      out.push({
        id: `${item.path}::${nextTrail.join('/')}`,
        title: item.title,
        path: item.path,
        category,
        module: mod,
        breadcrumbs: nextTrail.slice(0, -1),
        keywords: [...nextTrail, item.path, category, mod || ''].join(' ').toLowerCase(),
      })
    }
    if (item.children?.length) {
      walk(item.children, category, mod, nextTrail, out)
    }
  }
}

/** All leaf screens from the GYOROOM menu (plus role dashboard & apps center). */
export function buildAppsCatalog(tenantName = 'Hotel', user?: {
  is_superuser?: boolean
  role?: string
  home_path?: string
  rbac?: { home_path?: string }
} | null): AppTile[] {
  const menu = getGyoroomMenu(tenantName)
  const out: AppTile[] = []

  const dashPath = homePathForUser(user) || '/home'
  out.push({
    id: 'dashboard',
    title: 'My Dashboard',
    path: dashPath,
    category: 'Home',
    module: null,
    breadcrumbs: [],
    keywords: 'dashboard home overview',
  })
  out.push({
    id: 'apps-center',
    title: 'Apps Center',
    path: '/apps',
    category: 'Home',
    module: null,
    breadcrumbs: [],
    keywords: 'apps center launcher modules all items',
  })

  for (const section of menu) {
    if (section.title === 'Dashboard') continue
    const mod = SIDEBAR_MODULE_MAP[section.title] ?? section.module ?? null
    if (section.path) {
      out.push({
        id: section.path,
        title: section.title,
        path: section.path,
        category: section.title,
        module: mod,
        breadcrumbs: [],
        keywords: `${section.title} ${section.path}`.toLowerCase(),
      })
    }
    if (section.children) {
      walk(section.children, section.title, mod, [section.title], out)
    }
  }

  // Dedupe by path+title (same path can appear once)
  const seen = new Set<string>()
  return out.filter((app) => {
    const key = `${app.path}|${app.title}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

export function filterAppsForUser(
  apps: AppTile[],
  opts: {
    enabledModules?: string[] | null
    role?: string | null
    isSuperuser?: boolean
  }
): AppTile[] {
  const { enabledModules, role, isSuperuser } = opts
  if (isSuperuser) return apps

  return apps.filter((app) => {
    if (app.category === 'Home' || !app.module) {
      if (app.category !== 'Home' && app.category !== 'Dashboard') {
        if (!roleAllowsMenuSection(role, app.category, isSuperuser)) return false
      }
      return true
    }
    if (!roleAllowsMenuSection(role, app.category, isSuperuser)) return false
    if (enabledModules === undefined || enabledModules === null) return true
    if (enabledModules.length === 0) return app.category === 'Home'
    return enabledModules.includes(app.module)
  })
}

export const CATEGORY_COLORS: Record<string, string> = {
  Home: '#0f766e',
  FRONTDESK: '#2563eb',
  HOUSEKEEPING: '#059669',
  BANQUET: '#7c3aed',
  'F&B AND REVENUE CENTER': '#c2410c',
  'FOOD & BEVERAGE': '#c2410c',
  'RECIPE MANAGEMENT': '#ea580c',
  ACCOUNTS: '#7c3aed',
  INVENTORY: '#b45309',
  'SALES & MARKETING': '#db2777',
  'HUMAN RESOURCES': '#0284c7',
  HR: '#0284c7',
  'ASSET & MAINTANANCE': '#64748b',
  'ASSET & MAINTENANCE': '#64748b',
  'BROADCAST MESSAGE': '#4f46e5',
  'CHANNEL MANAGER': '#0d9488',
  'REPORT CENTER': '#334155',
  UTILITIES: '#475569',
  LAUNDRY: '#0ea5e9',
  'SPA & SALON': '#d946ef',
  'HALL ROOM': '#8b5cf6',
  POOL: '#06b6d4',
  WEBSITE: '#16a34a',
}

export function categoryColor(category: string) {
  return CATEGORY_COLORS[category] || '#64748b'
}
