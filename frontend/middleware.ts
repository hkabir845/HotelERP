import { NextRequest, NextResponse } from 'next/server'

/**
 * Platform apex hosts → ERP / login / SaaS (not tenant marketing sites).
 * Tenant public sites:
 *   - /site/{subdomain} on platform hosts
 *   - {subdomain}.{PLATFORM_ROOT_DOMAIN}  e.g. turag.sascorporationbd.com
 *   - custom domain on tenant.domain      e.g. turagwaterfrontresort.com
 */
const PLATFORM_ROOT = (
  process.env.NEXT_PUBLIC_PLATFORM_ROOT_DOMAIN || 'sascorporationbd.com'
)
  .trim()
  .toLowerCase()
  .replace(/^\.+|\.+$/g, '')

const PLATFORM_HOSTS = new Set(
  (
    process.env.NEXT_PUBLIC_PLATFORM_HOSTS ||
    `localhost,127.0.0.1,${PLATFORM_ROOT},www.${PLATFORM_ROOT}`
  )
    .split(',')
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean)
)

const RESERVED_SUBS = new Set([
  'www',
  'app',
  'api',
  'admin',
  'saas',
  'mail',
  'ftp',
  'static',
  'cdn',
])

const SKIP_PREFIXES = [
  '/api',
  '/_next',
  '/site',
  '/login',
  '/saas',
  '/home',
  '/apps',
  '/access-denied',
  '/fnb',
  '/frontdesk',
  '/housekeeping',
  '/accounts',
  '/inventory',
  '/assets',
  '/broadcast',
  '/reports',
  '/utilities',
  '/settings',
  '/hr',
  '/crm',
  '/banquet',
]

function shouldSkip(pathname: string): boolean {
  return SKIP_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`))
}

function tenantSubFromPlatformHost(hostname: string): string | null {
  if (!PLATFORM_ROOT || hostname === PLATFORM_ROOT || hostname === `www.${PLATFORM_ROOT}`) {
    return null
  }
  const suffix = `.${PLATFORM_ROOT}`
  if (!hostname.endsWith(suffix)) return null
  const sub = hostname.slice(0, -suffix.length)
  if (!sub || sub.includes('.') || RESERVED_SUBS.has(sub)) return null
  return sub
}

function rewriteToSite(request: NextRequest, sub: string, pathname: string) {
  let target = `/site/${sub}`
  if (pathname === '/book' || pathname.startsWith('/book/')) {
    target = `/site/${sub}/book`
  } else if (pathname === '/order' || pathname.startsWith('/order/')) {
    target = `/site/${sub}/order`
  } else if (pathname === '/' || pathname === '') {
    target = `/site/${sub}`
  } else if (!pathname.startsWith('/site/')) {
    // Keep marketing home for unknown paths on tenant hosts
    target = `/site/${sub}`
  }

  const rewriteUrl = request.nextUrl.clone()
  rewriteUrl.pathname = target
  const res = NextResponse.rewrite(rewriteUrl)
  res.headers.set('x-tenant-subdomain', sub)
  return res
}

export async function middleware(request: NextRequest) {
  const hostHeader = request.headers.get('host') || ''
  const hostname = hostHeader.split(':')[0].toLowerCase()
  const { pathname } = request.nextUrl

  if (shouldSkip(pathname)) {
    return NextResponse.next()
  }

  // Platform apex / localhost → normal app routes
  if (PLATFORM_HOSTS.has(hostname)) {
    return NextResponse.next()
  }

  // Fast path: {tenant}.sascorporationbd.com → /site/{tenant}
  const platformSub = tenantSubFromPlatformHost(hostname)
  if (platformSub) {
    return rewriteToSite(request, platformSub, pathname)
  }

  // Custom brand domain → resolve via API
  try {
    const apiBase = process.env.DJANGO_API_URL || 'http://127.0.0.1:8000'
    const url = `${apiBase}/api/public/resolve?host=${encodeURIComponent(hostHeader)}`
    const res = await fetch(url, { headers: { Accept: 'application/json' } })
    if (!res.ok) return NextResponse.next()
    const data = await res.json()
    const sub = data?.subdomain
    if (!sub) return NextResponse.next()
    return rewriteToSite(request, String(sub).toLowerCase(), pathname)
  } catch {
    return NextResponse.next()
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
