/** Frontend RBAC — mirrors backend/api/rbac.py (keep in sync). */

import type { ModuleKey } from './modules'

export type HotelRole =
  | 'superadmin'
  | 'admin'
  | 'operations_manager'
  | 'manager'
  | 'frontdesk'
  | 'housekeeping'
  | 'restaurant'
  | 'fnb'
  | 'accountant'
  | 'purchase_officer'
  | 'maintenance'
  | 'staff'

export interface RoleDef {
  key: HotelRole
  label: string
  description: string
  homePath: string
  modules: ModuleKey[] | null
  menuSections: string[] | null
  color: string
  demoEmail?: string
}

const ALL: ModuleKey[] = [
  'frontdesk',
  'housekeeping',
  'fnb',
  'recipes',
  'laundry',
  'spa',
  'hall',
  'banquet',
  'pool',
  'crm',
  'accounts',
  'inventory',
  'assets',
  'broadcast',
  'hr',
  'channel',
  'reports',
  'utilities',
  'landing',
]

export const ROLE_CATALOG: Record<string, RoleDef> = {
  superadmin: {
    key: 'superadmin',
    label: 'Platform Superadmin',
    description: 'SaaS control plane',
    homePath: '/saas',
    modules: ALL,
    menuSections: null,
    color: '#6366f1',
  },
  admin: {
    key: 'admin',
    label: 'Property Administrator',
    description: 'Full property access',
    homePath: '/home',
    modules: ALL,
    menuSections: null,
    color: '#0f766e',
    demoEmail: 'admin@admin.com',
  },
  operations_manager: {
    key: 'operations_manager',
    label: 'Operations Manager',
    description: 'Rooms, F&B, inventory, assets, CRM, reports',
    homePath: '/home/operations',
    modules: [
      'frontdesk',
      'housekeeping',
      'fnb',
      'recipes',
      'laundry',
      'spa',
      'hall',
      'banquet',
      'pool',
      'crm',
      'inventory',
      'assets',
      'broadcast',
      'reports',
      'channel',
    ],
    menuSections: [
      'Dashboard',
      'FRONTDESK',
      'HOUSEKEEPING',
      'BANQUET',
      'F&B AND REVENUE CENTER',
      'INVENTORY',
      'SALES & MARKETING',
      'ASSET & MAINTANANCE',
      'ASSET & MAINTENANCE',
      'BROADCAST MESSAGE',
      'CHANNEL MANAGER',
      'REPORT CENTER',
    ],
    color: '#1d4ed8',
    demoEmail: 'ops@turag.com',
  },
  manager: {
    key: 'manager',
    label: 'Manager',
    description: 'Operations oversight',
    homePath: '/home/operations',
    modules: null,
    menuSections: null,
    color: '#1d4ed8',
  },
  frontdesk: {
    key: 'frontdesk',
    label: 'Front Desk',
    description: 'Reservations, folio, room rack',
    homePath: '/home/frontdesk',
    modules: ['frontdesk', 'housekeeping', 'crm', 'broadcast', 'reports', 'channel'],
    menuSections: [
      'Dashboard',
      'FRONTDESK',
      'HOUSEKEEPING',
      'SALES & MARKETING',
      'BROADCAST MESSAGE',
      'CHANNEL MANAGER',
      'REPORT CENTER',
    ],
    color: '#2563eb',
    demoEmail: 'frontdesk@turag.com',
  },
  housekeeping: {
    key: 'housekeeping',
    label: 'Housekeeping',
    description: 'Room status, tasks, lost & found',
    homePath: '/home/housekeeping',
    modules: ['housekeeping', 'laundry', 'assets', 'reports'],
    menuSections: [
      'Dashboard',
      'HOUSEKEEPING',
      'LAUNDRY',
      'ASSET & MAINTANANCE',
      'ASSET & MAINTENANCE',
      'REPORT CENTER',
    ],
    color: '#059669',
    demoEmail: 'hk@turag.com',
  },
  restaurant: {
    key: 'restaurant',
    label: 'Restaurant / F&B',
    description: 'POS, menu, kitchen stock',
    homePath: '/home/restaurant',
    modules: ['fnb', 'recipes', 'inventory', 'reports'],
    menuSections: [
      'Dashboard',
      'F&B AND REVENUE CENTER',
      'FOOD & BEVERAGE',
      'RECIPE MANAGEMENT',
      'INVENTORY',
      'REPORT CENTER',
    ],
    color: '#c2410c',
    demoEmail: 'restaurant@turag.com',
  },
  fnb: {
    key: 'fnb',
    label: 'F&B',
    description: 'Restaurant POS',
    homePath: '/home/restaurant',
    modules: null,
    menuSections: null,
    color: '#c2410c',
  },
  accountant: {
    key: 'accountant',
    label: 'Accountant',
    description: 'Ledgers, vouchers, financial reports',
    homePath: '/home/accountant',
    modules: ['accounts', 'reports'],
    menuSections: ['Dashboard', 'ACCOUNTS', 'REPORT CENTER'],
    color: '#7c3aed',
    demoEmail: 'accountant@turag.com',
  },
  purchase_officer: {
    key: 'purchase_officer',
    label: 'Purchase Officer',
    description: 'POs, suppliers, stock — no GL posting',
    homePath: '/home/purchase',
    modules: ['inventory', 'reports'],
    menuSections: ['Dashboard', 'INVENTORY', 'REPORT CENTER'],
    color: '#b45309',
    demoEmail: 'purchase@turag.com',
  },
  maintenance: {
    key: 'maintenance',
    label: 'Maintenance',
    description: 'Assets & work orders',
    homePath: '/home/housekeeping',
    modules: ['assets', 'housekeeping', 'reports'],
    menuSections: [
      'Dashboard',
      'HOUSEKEEPING',
      'ASSET & MAINTANANCE',
      'ASSET & MAINTENANCE',
      'REPORT CENTER',
    ],
    color: '#64748b',
  },
  staff: {
    key: 'staff',
    label: 'Staff',
    description: 'Minimal access',
    homePath: '/home',
    modules: [],
    menuSections: ['Dashboard'],
    color: '#6b7280',
  },
}

const ALIAS: Record<string, string> = {
  manager: 'operations_manager',
  fnb: 'restaurant',
}

export function resolveRole(role?: string | null): RoleDef {
  const key = (role || 'staff').toLowerCase()
  const resolved = ALIAS[key] || key
  const base = ROLE_CATALOG[resolved] || ROLE_CATALOG.staff
  const self = ROLE_CATALOG[key]
  if (self && ALIAS[key]) {
    return { ...base, key: self.key, label: self.label }
  }
  return { ...base, key: (base.key || resolved) as HotelRole }
}

export function homePathForUser(user?: {
  is_superuser?: boolean
  role?: string
  home_path?: string
  rbac?: { home_path?: string }
} | null) {
  if (!user) return '/login'
  if (user.is_superuser) return '/saas'
  return user.home_path || user.rbac?.home_path || resolveRole(user.role).homePath
}

export function roleAllowsMenuSection(
  role: string | undefined | null,
  sectionTitle: string,
  isSuperuser?: boolean
) {
  if (isSuperuser) return true
  const def = resolveRole(role)
  if (def.key === 'admin' || def.key === 'superadmin') return true
  const sections = def.menuSections
  if (sections === null) return true
  if (!sections.length) return sectionTitle === 'Dashboard'
  return sections.some((s) => s.toLowerCase() === sectionTitle.toLowerCase())
}

export function DEMO_ROLE_LOGINS() {
  return [
    ROLE_CATALOG.admin,
    ROLE_CATALOG.operations_manager,
    ROLE_CATALOG.frontdesk,
    ROLE_CATALOG.housekeeping,
    ROLE_CATALOG.restaurant,
    ROLE_CATALOG.accountant,
    ROLE_CATALOG.purchase_officer,
  ].filter((r) => r.demoEmail)
}

/** Map app URL prefixes to SaaS module keys (mirrors API RBAC). */
export function moduleForAppPath(pathname: string): ModuleKey | 'utilities' | null {
  const path = pathname || ''
  if (path.startsWith('/login') || path.startsWith('/saas') || path.startsWith('/site') || path.startsWith('/access-denied') || path.startsWith('/apps')) {
    return null
  }
  if (path.startsWith('/home')) return null
  if (path.startsWith('/accounts')) return 'accounts'
  if (path.startsWith('/inventory')) return 'inventory'
  if (path.startsWith('/fnb')) return 'fnb'
  if (path.startsWith('/housekeeping')) return 'housekeeping'
  if (path.startsWith('/frontdesk') || path.startsWith('/reservations')) return 'frontdesk'
  if (path.startsWith('/banquet')) return 'banquet'
  if (path.startsWith('/hr')) return 'hr'
  if (path.startsWith('/crm') || path.startsWith('/sales')) return 'crm'
  if (path.startsWith('/assets')) return 'assets'
  if (path.startsWith('/broadcast')) return 'broadcast'
  if (path.startsWith('/utilities') || path.startsWith('/website')) return 'utilities'
  if (path.startsWith('/reports')) return 'reports'
  if (path.startsWith('/channel')) return 'channel'
  return null
}

export function userHasModuleAccess(
  user: { is_superuser?: boolean; role?: string; enabled_modules?: string[] } | null | undefined,
  moduleKey: string
) {
  if (!user) return false
  if (user.is_superuser) return true
  const role = (user.role || '').toLowerCase()
  if (role === 'admin' || role === 'superadmin') return true
  const mods = user.enabled_modules
  if (mods === undefined || mods === null) return true
  return mods.includes(moduleKey)
}
