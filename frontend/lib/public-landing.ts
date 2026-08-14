import type { Metadata } from 'next'
import { mergeLandingContent, type LandingContent } from '@/lib/landings/turag-content'

export type PublicLanding = {
  name: string
  subdomain: string
  domain?: string | null
  public_urls?: {
    path?: string
    saas?: string | null
    custom?: string | null
  }
  product_type: string
  logo?: string | null
  landing_enabled: boolean
  landing_title: string
  landing_tagline?: string | null
  landing_template?: string
  content?: Partial<LandingContent> | Record<string, unknown>
  seo?: {
    title?: string
    description?: string
    keywords?: string
    og_image?: string
  }
  city?: string | null
  country?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  subscription_active?: boolean
  updated_at?: string | null
  ctas?: { book?: boolean; order?: boolean; login?: boolean }
  room_types?: PublicRoomType[]
  menu?: PublicMenuItem[]
  tables?: PublicTable[]
  rooms?: PublicRoom[]
}

export type PublicRoomType = {
  id: number
  name: string
  description?: string
  max_occupancy?: number
  base_rate?: number
  amenities?: string
  room_count?: number
  available_rooms?: number
}

export type PublicMenuItem = {
  id: number
  name: string
  description?: string
  price: number
  category: string
  image?: string | null
}

export type PublicTable = {
  id: number
  table_number: string
  capacity: number
  location?: string
}

export type PublicRoom = {
  id: number
  room_number: string
  room_type?: string
}

export function siteOrigin() {
  return (process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000').replace(/\/$/, '')
}

export function platformRootDomain() {
  return (process.env.NEXT_PUBLIC_PLATFORM_ROOT_DOMAIN || 'sascorporationbd.com')
    .trim()
    .toLowerCase()
    .replace(/^\.+|\.+$/g, '')
}

/** Preferred public absolute URL (SaaS subdomain, then custom domain, then path). */
export function preferredPublicUrl(tenant: Pick<PublicLanding, 'subdomain' | 'domain' | 'public_urls'>) {
  const urls = tenant.public_urls
  if (urls?.saas) return urls.saas.replace(/\/$/, '')
  if (urls?.custom) return urls.custom.replace(/\/$/, '')
  const root = platformRootDomain()
  const sub = (tenant.subdomain || '').toLowerCase()
  if (sub && root) return `https://${sub}.${root}`
  if (tenant.domain) {
    const d = tenant.domain.replace(/^www\./i, '')
    return `https://${d}`
  }
  return `${siteOrigin()}/site/${sub}`
}

/**
 * In-app path prefix for links on the public site.
 * On tenant hosts (saas/custom) use ''; on platform hosts use /site/{sub}.
 */
export function publicSiteBasePath(
  subdomain: string,
  opts?: { domain?: string | null; host?: string | null }
) {
  const sub = (subdomain || '').toLowerCase()
  const host = (opts?.host || '').split(':')[0].toLowerCase()
  const root = platformRootDomain()
  const custom = (opts?.domain || '').toLowerCase().replace(/^www\./, '')

  if (host) {
    if (root && host === `${sub}.${root}`) return ''
    if (custom && (host === custom || host === `www.${custom}`)) return ''
  }
  return `/site/${sub}`
}

export function djangoApiBase() {
  return (process.env.DJANGO_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
}

export function absoluteAsset(path?: string | null) {
  if (!path) return undefined
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return `${siteOrigin()}${path.startsWith('/') ? path : `/${path}`}`
}

export async function fetchPublicLanding(subdomain: string): Promise<PublicLanding | null> {
  try {
    const res = await fetch(`${djangoApiBase()}/api/public/landing/${subdomain}`, {
      next: { revalidate: 30 },
    })
    if (!res.ok) return null
    return (await res.json()) as PublicLanding
  } catch {
    return null
  }
}

export async function fetchPublicSites(): Promise<
  { subdomain: string; domain?: string | null; name: string; updated_at?: string | null }[]
> {
  try {
    const res = await fetch(`${djangoApiBase()}/api/public/sites`, { next: { revalidate: 60 } })
    if (!res.ok) return []
    const data = await res.json()
    return data.sites || []
  } catch {
    return []
  }
}

export function landingContentFor(tenant: PublicLanding): LandingContent {
  const merged = mergeLandingContent(tenant.content)
  if (tenant.landing_title) merged.brand = tenant.landing_title
  if (tenant.landing_tagline) merged.tagline = tenant.landing_tagline
  if (tenant.logo) merged.images.logo = tenant.logo
  return merged
}

export function metadataForLanding(tenant: PublicLanding, subdomain: string): Metadata {
  const seo = tenant.seo || {}
  const title = seo.title || tenant.landing_title || tenant.name
  const description = seo.description || tenant.landing_tagline || `${tenant.name} official website`
  const ogImage = absoluteAsset(seo.og_image || tenant.logo || undefined)
  const canonical = preferredPublicUrl({ ...tenant, subdomain: tenant.subdomain || subdomain })
  const alternates = [
    `${siteOrigin()}/site/${tenant.subdomain || subdomain}`,
    tenant.public_urls?.saas,
    tenant.public_urls?.custom,
  ].filter(Boolean) as string[]
  return {
    title,
    description,
    keywords: seo.keywords ? seo.keywords.split(',').map((k) => k.trim()) : undefined,
    alternates: {
      canonical,
      // expose path + saas + custom as equivalent entry points
      languages: undefined,
    },
    robots: { index: true, follow: true },
    openGraph: {
      type: 'website',
      title,
      description,
      url: canonical,
      siteName: tenant.name,
      locale: 'en_US',
      images: ogImage ? [{ url: ogImage, alt: tenant.name }] : undefined,
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: ogImage ? [ogImage] : undefined,
    },
    other: {
      'og:see_also': alternates.filter((u) => u !== canonical).join(','),
    },
  }
}

export function jsonLdForLanding(tenant: PublicLanding, content: LandingContent) {
  const url = preferredPublicUrl(tenant)
  return {
    '@context': 'https://schema.org',
    '@type': tenant.product_type === 'restaurant' ? 'Restaurant' : 'LodgingBusiness',
    name: tenant.name,
    description: tenant.seo?.description || tenant.landing_tagline || content.tagline,
    url,
    image: absoluteAsset(tenant.seo?.og_image || content.images.hero),
    logo: absoluteAsset(content.images.logo),
    telephone: tenant.phone || content.contact.phones[0],
    email: tenant.email || content.contact.emails[0],
    address: {
      '@type': 'PostalAddress',
      streetAddress: tenant.address || content.contact.resortAddress,
      addressLocality: tenant.city || undefined,
      addressCountry: tenant.country || undefined,
    },
    sameAs: [
      content.contact.facebook,
      tenant.public_urls?.saas,
      tenant.public_urls?.custom,
      content.contact.website,
      `${siteOrigin()}/site/${tenant.subdomain}`,
    ].filter(Boolean),
  }
}
