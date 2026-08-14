'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { Menu, X, MapPin, Phone, Mail, UtensilsCrossed, BedDouble } from 'lucide-react'
import type { PublicLanding } from '@/lib/public-landing'
import { formatMoney } from '@/lib/money'

type ThemeKey = 'hotel' | 'resort' | 'restaurant'

const THEMES: Record<
  ThemeKey,
  {
    ink: string
    cream: string
    deep: string
    accent: string
    muted: string
    hero: string
    eyebrow: string
  }
> = {
  hotel: {
    ink: '#0f172a',
    cream: '#f4f1ea',
    deep: '#1e293b',
    accent: '#b45309',
    muted: '#64748b',
    hero: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0f172a 100%)',
    eyebrow: 'Boutique hotel',
  },
  resort: {
    ink: '#16352d',
    cream: '#f7f4ee',
    deep: '#0f241f',
    accent: '#c4a35a',
    muted: '#5d6f68',
    hero: 'linear-gradient(135deg, #0f241f 0%, #16352d 50%, #1f4339 100%)',
    eyebrow: 'Resort by nature',
  },
  restaurant: {
    ink: '#3f1d12',
    cream: '#faf6f1',
    deep: '#2a140c',
    accent: '#c2410c',
    muted: '#7c5a4a',
    hero: 'linear-gradient(135deg, #2a140c 0%, #7c2d12 50%, #1c0f0a 100%)',
    eyebrow: 'Kitchen & dining',
  },
}

function themeFor(tenant: PublicLanding): ThemeKey {
  const t = (tenant.landing_template || '').toLowerCase()
  if (t === 'restaurant' || t === 'resort' || t === 'hotel') return t
  const p = (tenant.product_type || 'hotel').toLowerCase()
  if (p === 'restaurant') return 'restaurant'
  if (p === 'resort') return 'resort'
  return 'hotel'
}

export default function HospitalitySite({
  tenant,
  subdomain,
  basePath = `/site/${subdomain}`,
}: {
  tenant: PublicLanding
  subdomain: string
  basePath?: string
}) {
  const key = themeFor(tenant)
  const theme = THEMES[key]
  const [menuOpen, setMenuOpen] = useState(false)
  const ctas = tenant.ctas || { book: key !== 'restaurant', order: true, login: true }
  const roomTypes = tenant.room_types || []
  const menu = tenant.menu || []
  const title = tenant.landing_title || tenant.name
  const tagline =
    tenant.landing_tagline ||
    (key === 'restaurant'
      ? 'Seasonal cooking, warm service, tables or room delivery.'
      : key === 'resort'
        ? 'Stay among nature. Dine well. Book your own dates.'
        : 'Comfortable rooms, in-house restaurant, honest rates.')

  const featuredMenu = useMemo(() => menu.slice(0, 6), [menu])
  const location = [tenant.address, tenant.city, tenant.country].filter(Boolean).join(', ')

  const nav = [
    { href: '#home', label: 'Home' },
    ...(roomTypes.length ? [{ href: '#stay', label: 'Stay' }] : []),
    ...(menu.length ? [{ href: '#dine', label: 'Dine' }] : []),
    { href: '#contact', label: 'Contact' },
  ]

  return (
    <div className="min-h-screen antialiased" style={{ background: theme.cream, color: theme.ink }}>
      <header
        className="sticky top-0 z-40 border-b backdrop-blur-md"
        style={{ background: `${theme.cream}f2`, borderColor: `${theme.ink}14` }}
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <a href="#home" className="flex min-w-0 items-center gap-3">
            {tenant.logo ? (
              <span className="inline-flex rounded-xl px-2 py-1" style={{ background: theme.cream }}>
                <img src={tenant.logo} alt={tenant.name} className="h-12 w-auto max-w-[200px] object-contain" />
              </span>
            ) : (
              <span className="truncate text-lg font-semibold">{tenant.name}</span>
            )}
          </a>
          <nav className="hidden items-center gap-6 text-sm font-medium md:flex">
            {nav.map((item) => (
              <a key={item.href} href={item.href} className="hover:opacity-70">
                {item.label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            {ctas.book && (
              <Link
                href={`${basePath}/book`}
                className="hidden min-h-[44px] items-center rounded-full px-4 py-2 text-sm font-medium text-white sm:inline-flex"
                style={{ background: theme.ink }}
              >
                Book stay
              </Link>
            )}
            {ctas.order && (
              <Link
                href={`${basePath}/order`}
                className="inline-flex min-h-[44px] items-center rounded-full px-4 py-2 text-sm font-medium text-white"
                style={{ background: theme.accent }}
              >
                Order food
              </Link>
            )}
            <button
              type="button"
              className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-full border md:hidden"
              style={{ borderColor: `${theme.ink}22` }}
              onClick={() => setMenuOpen((v) => !v)}
              aria-label="Menu"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {menuOpen && (
          <div className="border-t px-4 py-3 md:hidden" style={{ borderColor: `${theme.ink}14` }}>
            {nav.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="block min-h-[44px] py-3 text-sm"
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </a>
            ))}
          </div>
        )}
      </header>

      <section id="home" className="relative overflow-hidden text-white" style={{ background: theme.hero }}>
        <div className="mx-auto flex min-h-[72vh] max-w-6xl flex-col justify-center px-4 py-16 sm:px-6">
          <p className="text-xs uppercase tracking-[0.28em] text-white/70">{theme.eyebrow}</p>
          <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight sm:text-6xl">{title}</h1>
          <p className="mt-4 max-w-2xl text-base text-white/80 sm:text-lg">{tagline}</p>
          {location && (
            <p className="mt-3 flex items-center gap-2 text-sm text-white/65">
              <MapPin className="h-4 w-4" /> {location}
            </p>
          )}
          {!tenant.subscription_active && (
            <p className="mt-4 max-w-xl rounded-lg border border-amber-300/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-100">
              Online booking and ordering may be paused while the subscription is renewed.
            </p>
          )}
          <div className="mt-8 flex flex-wrap gap-3">
            {ctas.book && (
              <Link
                href={`${basePath}/book`}
                className="inline-flex min-h-[44px] items-center rounded-full bg-white px-6 py-3 text-sm font-semibold"
                style={{ color: theme.ink }}
              >
                Check availability
              </Link>
            )}
            {ctas.order && (
              <Link
                href={`${basePath}/order`}
                className="inline-flex min-h-[44px] items-center rounded-full border border-white/40 px-6 py-3 text-sm font-medium text-white"
              >
                Order to room or table
              </Link>
            )}
          </div>
        </div>
      </section>

      {roomTypes.length > 0 && (
        <section id="stay" className="px-4 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto max-w-6xl">
            <p className="text-xs uppercase tracking-[0.28em]" style={{ color: theme.muted }}>
              From the booking engine
            </p>
            <h2 className="mt-2 text-3xl font-semibold sm:text-4xl">Accommodations</h2>
            <p className="mt-3 max-w-2xl text-sm" style={{ color: theme.muted }}>
              Live room types and rates from the property ERP. Guests book the same inventory the front desk uses.
            </p>
            <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {roomTypes.map((rt) => (
                <article
                  key={rt.id}
                  className="flex flex-col rounded-2xl border bg-white p-5 shadow-sm"
                  style={{ borderColor: `${theme.ink}12` }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-xl font-semibold">{rt.name}</h3>
                    <BedDouble className="h-5 w-5 shrink-0 opacity-40" />
                  </div>
                  <p className="mt-2 flex-1 text-sm" style={{ color: theme.muted }}>
                    {rt.description || `Sleeps ${rt.max_occupancy}. ${rt.amenities || ''}`}
                  </p>
                  <p className="mt-4 text-xs" style={{ color: theme.muted }}>
                    Up to {rt.max_occupancy} guests
                    {rt.room_count ? ` · ${rt.room_count} rooms` : ''}
                  </p>
                  <div className="mt-4 flex items-end justify-between">
                    <p className="text-2xl font-semibold">
                      {formatMoney(rt.base_rate || 0, { digits: 0 })}
                      <span className="text-sm font-normal opacity-60"> / night</span>
                    </p>
                    {ctas.book && (
                      <Link
                        href={`${basePath}/book?room_type=${rt.id}`}
                        className="text-sm font-medium underline-offset-4 hover:underline"
                        style={{ color: theme.accent }}
                      >
                        Reserve
                      </Link>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {menu.length > 0 && (
        <section id="dine" className="px-4 py-16 text-white sm:px-6 sm:py-20" style={{ background: theme.deep }}>
          <div className="mx-auto max-w-6xl">
            <p className="text-xs uppercase tracking-[0.28em] text-white/60">From the kitchen</p>
            <h2 className="mt-2 text-3xl font-semibold sm:text-4xl">Dining</h2>
            <p className="mt-3 max-w-2xl text-sm text-white/70">
              The public menu is the same catalog used at the restaurant POS. Order to a table or to a guest room, with
              a serve time you choose.
            </p>
            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {featuredMenu.map((item) => (
                <article key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-medium">{item.name}</h3>
                    <UtensilsCrossed className="h-4 w-4 opacity-50" />
                  </div>
                  <p className="mt-2 line-clamp-2 text-sm text-white/65">{item.description}</p>
                  <p className="mt-4 text-lg font-semibold">{formatMoney(item.price)}</p>
                </article>
              ))}
            </div>
            {ctas.order && (
              <Link
                href={`${basePath}/order`}
                className="mt-8 inline-flex min-h-[44px] items-center rounded-full bg-white px-6 py-3 text-sm font-semibold"
                style={{ color: theme.ink }}
              >
                Place a food order
              </Link>
            )}
          </div>
        </section>
      )}

      <section id="contact" className="px-4 py-16 sm:px-6">
        <div className="mx-auto grid max-w-6xl gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border bg-white p-5" style={{ borderColor: `${theme.ink}12` }}>
            <p className="text-xs uppercase tracking-wider" style={{ color: theme.muted }}>
              Phone
            </p>
            <p className="mt-2 flex items-center gap-2 text-sm">
              <Phone className="h-4 w-4" /> {tenant.phone || '—'}
            </p>
          </div>
          <div className="rounded-2xl border bg-white p-5" style={{ borderColor: `${theme.ink}12` }}>
            <p className="text-xs uppercase tracking-wider" style={{ color: theme.muted }}>
              Email
            </p>
            <p className="mt-2 flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4" /> {tenant.email || '—'}
            </p>
          </div>
          <div className="rounded-2xl border bg-white p-5" style={{ borderColor: `${theme.ink}12` }}>
            <p className="text-xs uppercase tracking-wider" style={{ color: theme.muted }}>
              Address
            </p>
            <p className="mt-2 text-sm">{location || '—'}</p>
          </div>
        </div>
      </section>

      <footer className="border-t px-4 py-8 text-center text-xs" style={{ borderColor: `${theme.ink}14`, color: theme.muted }}>
        {tenant.name} · Powered by the property ERP ·{' '}
        <Link href={`/login?site=${subdomain}`} className="underline-offset-2 hover:underline">
          Staff login
        </Link>
      </footer>
    </div>
  )
}
