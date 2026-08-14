/** SaaS module catalog and product presets (mirrors backend). */

export type ProductType = 'hotel' | 'resort' | 'restaurant' | 'mixed'

export const ALL_MODULES = [
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
] as const

export type ModuleKey = (typeof ALL_MODULES)[number]

export const MODULE_LABELS: Record<ModuleKey, string> = {
  frontdesk: 'Frontdesk / Reservations',
  housekeeping: 'Housekeeping',
  fnb: 'Food & Beverage / Restaurant POS',
  recipes: 'Recipe Management / Kitchen Stock',
  laundry: 'Laundry POS',
  spa: 'Spa & Beauty Salon',
  hall: 'Hall Room',
  banquet: 'Banquet / Events',
  pool: 'Pool Booking',
  crm: 'Sales & Marketing / CRM',
  accounts: 'Accounts',
  inventory: 'Inventory',
  assets: 'Asset & Maintenance',
  broadcast: 'Broadcast Messaging',
  hr: 'HR / Employees',
  channel: 'Channel Manager',
  reports: 'Report Center',
  utilities: 'Utilities / Settings',
  landing: 'Public Landing Page',
}

export const PRODUCT_TYPES: { key: ProductType; label: string }[] = [
  { key: 'hotel', label: 'Hotel (includes restaurant)' },
  { key: 'resort', label: 'Resort (includes restaurant)' },
  { key: 'restaurant', label: 'Restaurant only' },
  { key: 'mixed', label: 'Hotel + Restaurant' },
]

const STAY_MODULES: ModuleKey[] = [
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

const RESTAURANT_MODULES: ModuleKey[] = [
  'fnb',
  'recipes',
  'accounts',
  'inventory',
  'broadcast',
  'reports',
  'utilities',
  'landing',
]

export const MODULE_PRESETS: Record<ProductType, ModuleKey[]> = {
  hotel: [...STAY_MODULES],
  resort: [...STAY_MODULES],
  restaurant: [...RESTAURANT_MODULES],
  mixed: [...ALL_MODULES],
}

/** Modules shown for a subscription. Restaurant plans cannot enable hotel operations. */
export function modulesForProduct(productType: ProductType): ModuleKey[] {
  if (productType === 'restaurant') return [...RESTAURANT_MODULES]
  return [...ALL_MODULES]
}

export const WEBSITE_TEMPLATES: { key: string; label: string; product_types: ProductType[] }[] = [
  { key: 'hotel', label: 'Professional hotel', product_types: ['hotel', 'mixed'] },
  { key: 'resort', label: 'Professional resort', product_types: ['resort', 'mixed'] },
  { key: 'restaurant', label: 'Professional restaurant', product_types: ['restaurant', 'hotel', 'resort', 'mixed'] },
  { key: 'turag', label: 'Turag Waterfront (signature)', product_types: ['resort', 'mixed'] },
]

export function defaultWebsiteTemplate(productType: ProductType, subdomain = '') {
  if (subdomain.toLowerCase() === 'turag') return 'turag'
  if (productType === 'restaurant') return 'restaurant'
  if (productType === 'resort') return 'resort'
  return 'hotel'
}

/** Map sidebar section titles to module keys */
export const SIDEBAR_MODULE_MAP: Record<string, ModuleKey | null> = {
  Dashboard: null,
  'Apps Center': null,
  FRONTDESK: 'frontdesk',
  HOUSEKEEPING: 'housekeeping',
  LAUNDRY: 'laundry',
  'SPA & SALON': 'spa',
  'HALL ROOM': 'hall',
  BANQUET: 'banquet',
  POOL: 'pool',
  'FOOD & BEVERAGE': 'fnb',
  'F&B AND REVENUE CENTER': 'fnb',
  'RECIPE MANAGEMENT': 'recipes',
  ACCOUNTS: 'accounts',
  INVENTORY: 'inventory',
  'SALES & MARKETING': 'crm',
  'HUMAN RESOURCES': 'hr',
  'ASSET & MAINTENANCE': 'assets',
  'ASSET & MAINTANANCE': 'assets',
  'BROADCAST MESSAGE': 'broadcast',
  HR: 'hr',
  'CHANNEL MANAGER': 'channel',
  FORECAST: 'frontdesk',
  RATE: 'frontdesk',
  'REPORT CENTER': 'reports',
  UTILITIES: 'utilities',
  WEBSITE: 'landing',
}

export function hasModule(enabled: string[] | undefined | null, key: ModuleKey): boolean {
  // undefined/null = unknown (legacy) → allow; explicit [] = no modules
  if (enabled === undefined || enabled === null) return true
  if (enabled.length === 0) return false
  return enabled.includes(key)
}
