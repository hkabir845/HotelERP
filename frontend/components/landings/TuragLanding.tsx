'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Cormorant_Garamond, Outfit } from 'next/font/google'
import { TURAG_CONTENT, type LandingContent } from '@/lib/landings/turag-content'
import TuragLogo from '@/components/landings/TuragLogo'
import TuragHeroSlideshow from '@/components/landings/TuragHeroSlideshow'
import { Menu, X } from 'lucide-react'
import type { PublicMenuItem, PublicRoomType } from '@/lib/public-landing'
import { formatMoney } from '@/lib/money'

const display = Cormorant_Garamond({
  subsets: ['latin'],
  weight: ['500', '600', '700'],
  variable: '--font-turag-display',
  display: 'swap',
  fallback: ['Georgia', 'serif'],
})

const sans = Outfit({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-turag-sans',
  display: 'swap',
  fallback: ['system-ui', 'sans-serif'],
})

type Props = {
  subdomain: string
  /** '' on custom/saas host; '/site/turag' on platform hosts */
  basePath?: string
  ctas?: { book?: boolean; order?: boolean; login?: boolean }
  subscriptionActive?: boolean
  content?: LandingContent
  roomTypes?: PublicRoomType[]
  menuItems?: PublicMenuItem[]
}

export default function TuragLanding({
  subdomain,
  basePath = `/site/${subdomain}`,
  ctas,
  subscriptionActive = true,
  content,
  roomTypes,
}: Props) {
  const C = content || TURAG_CONTENT
  const [stayFilter, setStayFilter] = useState<string>('all')
  const [galleryFilter, setGalleryFilter] = useState<string>('all')
  const [menuOpen, setMenuOpen] = useState(false)
  const [contactForm, setContactForm] = useState({ name: '', email: '', phone: '', message: '' })
  const [contactStatus, setContactStatus] = useState('')
  const book = ctas?.book !== false
  const order = ctas?.order !== false

  const stays = (roomTypes && roomTypes.length
    ? roomTypes.map((rt) => {
        const match = C.accommodations.find(
          (a) =>
            rt.name.toLowerCase().includes(a.name.toLowerCase()) ||
            a.name.toLowerCase().includes(rt.name.toLowerCase().split(' ').pop() || '')
        )
        return {
          key: String(rt.id),
          name: rt.name,
          blurb: rt.description || match?.blurb || `Up to ${rt.max_occupancy || 2} guests`,
          image: match?.image || C.accommodations[0]?.image || C.images.cottage,
          rate: rt.base_rate,
        }
      })
    : C.accommodations.map((a) => ({ ...a, rate: undefined as number | undefined }))
  ).filter((a) => stayFilter === 'all' || a.key === stayFilter || a.name.toLowerCase() === stayFilter)

  const stayFilters = roomTypes && roomTypes.length
    ? roomTypes.map((rt) => ({ key: String(rt.id), name: rt.name }))
    : C.accommodations.map((a) => ({ key: a.key, name: a.name }))

  const galleryTypes = ['All', 'Outdoor', 'Dining', 'Activities', 'Rooms', 'Interior', 'Events']
  const galleryItems = (C.gallery || []).filter(
    (g) => galleryFilter === 'all' || (g.type || 'Outdoor') === galleryFilter
  )

  const submitContact = async (e: React.FormEvent) => {
    e.preventDefault()
    setContactStatus('Sending…')
    try {
      const res = await fetch(`/api/public/${subdomain}/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contactForm),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Could not send')
      setContactStatus(data.message || 'Thank you. We will contact you soon.')
      setContactForm({ name: '', email: '', phone: '', message: '' })
    } catch (err: any) {
      setContactStatus(err.message || 'Could not send message')
    }
  }

  return (
    <div
      className={`${display.variable} ${sans.variable} min-h-screen overflow-x-hidden text-[#1c2e28] antialiased`}
      style={{ fontFamily: 'var(--font-turag-sans), system-ui, sans-serif' }}
    >
      <style>{`
        @keyframes turag-rise {
          from { opacity: 0; transform: translateY(18px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes turag-fade {
          from { opacity: 0.7; }
          to { opacity: 1; }
        }
        .turag-rise { animation: turag-rise 0.9s ease-out both; }
        .turag-rise-delay { animation: turag-rise 1s ease-out 0.18s both; }
        .turag-logo-on-light img {
          filter: drop-shadow(0 1px 1px rgba(255,255,255,0.8));
        }
      `}</style>

      {/* Nav */}
      <header className="fixed inset-x-0 top-0 z-50 h-[4.75rem] border-b border-[#e4ddd0] bg-[#f7f4ee]/95 shadow-sm backdrop-blur-md sm:h-[5.75rem]">
        <div className="mx-auto flex h-full max-w-6xl items-center justify-between gap-3 px-4 sm:px-5">
          <TuragLogo
            href="#home"
            src={C.images.logo}
            heightClass="h-14 sm:h-[4.5rem]"
            className="transition-all"
          />
          <nav className="hidden items-center gap-6 text-sm font-medium text-[#16352d] md:flex" aria-label="Primary">
            {C.nav.map((item) => (
              <a key={item.id} href={`#${item.id}`} className="hover:text-[#c4a35a]">
                {item.label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            {book && (
              <Link
                href={`${basePath}/book`}
                className="inline-flex min-h-[44px] items-center rounded-full bg-[#c4a35a] px-4 py-2 text-sm font-medium text-[#1c2e28] hover:bg-[#d4b56a]"
              >
                {C.copy.ctaBook}
              </Link>
            )}
            <a
              href={C.contact.website}
              target="_blank"
              rel="noreferrer"
              className="hidden min-h-[44px] items-center rounded-full border border-[#16352d]/20 px-3 py-2 text-xs text-[#16352d] hover:bg-[#16352d]/5 sm:inline-flex"
            >
              {C.copy.liveSite}
            </a>
            <button
              type="button"
              className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-full border border-[#16352d]/20 text-[#16352d] md:hidden"
              aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((v) => !v)}
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {menuOpen && (
          <nav className="border-t border-[#e4ddd0] px-4 py-3 md:hidden" aria-label="Mobile">
            <div className="flex flex-col gap-1">
              {C.nav.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className="min-h-[44px] rounded-lg px-3 py-3 text-sm text-[#16352d] hover:bg-[#16352d]/5"
                  onClick={() => setMenuOpen(false)}
                >
                  {item.label}
                </a>
              ))}
            </div>
          </nav>
        )}
      </header>

      {/* Hero fills the first screen so the photo and 3 buttons are all visible at the top */}
      <section
        id="home"
        className="relative mt-[4.75rem] h-[calc(100dvh-4.75rem)] overflow-hidden bg-[#0f241f] sm:mt-[5.75rem] sm:h-[calc(100dvh-5.75rem)]"
      >
        <TuragHeroSlideshow
          className="h-full w-full"
          slides={
            C.heroSlides?.length
              ? C.heroSlides
              : [{ src: C.images.hero, alt: `${C.brand}, ${C.copy.heroLocation}` }]
          }
        />

        <div className="pointer-events-none absolute inset-0 z-10 flex items-end">
          <div className="pointer-events-auto flex w-full flex-col items-start justify-between gap-3 px-4 pb-5 pt-8 sm:flex-row sm:items-end sm:px-6 sm:pb-6 lg:px-8">
            <div>
              <h1
                className="turag-rise text-2xl font-semibold leading-tight text-white drop-shadow sm:text-4xl"
                style={{ fontFamily: 'var(--font-turag-display), serif' }}
              >
                {C.brand}
              </h1>
              <p className="turag-rise mt-1 text-xs uppercase tracking-[0.28em] text-emerald-100/90 sm:text-sm">
                {C.copy.heroLocation}
              </p>
              <p className="turag-rise-delay mt-2 text-sm text-white/90">{C.copy.heroPhones}</p>
            </div>
            <div className="turag-rise-delay flex flex-wrap items-center gap-3">
              {book && (
                <Link
                  href={`${basePath}/book`}
                  className="inline-flex min-h-[44px] items-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#16352d] shadow-lg hover:bg-emerald-50"
                >
                  {C.copy.ctaBook}
                </Link>
              )}
              {order && (
                <Link
                  href={`${basePath}/order`}
                  className="inline-flex min-h-[44px] items-center rounded-full border border-white/70 bg-transparent px-6 py-3 text-sm font-medium text-white hover:bg-white/15"
                >
                  {C.copy.ctaOrder}
                </Link>
              )}
              <a
                href="#about"
                className="inline-flex min-h-[44px] items-center px-2 py-3 text-sm font-medium text-white/90 hover:text-white"
              >
                {C.copy.ctaDiscover}
              </a>
            </div>
          </div>
        </div>
        {!subscriptionActive && (
          <p className="absolute bottom-1 left-4 z-10 text-xs text-amber-100 sm:left-6">
            Online booking may be limited while the subscription is pending renewal.
          </p>
        )}
      </section>

      {/* About */}
      <section id="about" className="relative bg-[#f3f0e8]">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-5 sm:py-20 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-[#5d6f68]">About</p>
            <h2
              className="mt-2 text-4xl font-semibold text-[#16352d] sm:text-5xl"
              style={{ fontFamily: 'var(--font-turag-display), serif' }}
            >
              {C.about.title}
            </h2>
            <p className="mt-5 text-base leading-relaxed text-[#3a4d46]">{C.about.body}</p>
            <p className="mt-4 text-base leading-relaxed text-[#3a4d46]">{C.shortPitch}</p>
          </div>
          <div className="relative overflow-hidden rounded-sm">
            <img
              src={C.images.about}
              alt="Aerial view of Turag Waterfront Resort cottages on the river"
              className="h-56 w-full object-cover sm:h-[360px] lg:h-[420px]"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#0f241f]/80 to-transparent p-5 text-sm text-white">
              {C.copy.aboutCaption}
            </div>
          </div>
        </div>

        <div className="mx-auto grid max-w-6xl gap-6 px-5 pb-16 md:grid-cols-2">
          <div className="border-l-2 border-[#c4a35a] bg-white/50 px-5 py-4">
            <h3
              className="text-2xl text-[#16352d]"
              style={{ fontFamily: 'var(--font-turag-display), serif' }}
            >
              {C.copy.ecoTitle}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-[#3a4d46]">{C.about.eco}</p>
          </div>
          <div className="border-l-2 border-[#2d6a5a] bg-white/50 px-5 py-4">
            <h3
              className="text-2xl text-[#16352d]"
              style={{ fontFamily: 'var(--font-turag-display), serif' }}
            >
              {C.copy.boutiqueTitle}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-[#3a4d46]">{C.about.boutique}</p>
          </div>
        </div>

        <div className="mx-auto grid max-w-6xl gap-8 px-5 pb-20 sm:grid-cols-2 lg:grid-cols-4">
          {C.highlights.map((h, i) => (
            <div key={h.title}>
              <p className="text-3xl font-light text-[#c4a35a]" style={{ fontFamily: 'var(--font-turag-display), serif' }}>
                0{i + 1}
              </p>
              <h4 className="mt-1 font-medium text-[#16352d]">{h.title}</h4>
              <p className="mt-1 text-sm text-[#5d6f68]">{h.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Accommodations */}
      <section id="stay" className="bg-[#16352d] text-white">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-5 sm:py-20">
          <p className="text-xs uppercase tracking-[0.28em] text-emerald-200/70">{C.copy.stayEyebrow}</p>
          <h2
            className="mt-2 text-3xl font-semibold sm:text-5xl"
            style={{ fontFamily: 'var(--font-turag-display), serif' }}
          >
            {C.copy.stayTitle}
          </h2>
          <p className="mt-4 max-w-2xl text-emerald-50/80">{C.copy.stayIntro}</p>

          <div className="mt-8 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setStayFilter('all')}
              className={`rounded-full px-4 py-1.5 text-sm ${
                stayFilter === 'all' ? 'bg-[#c4a35a] text-[#1c2e28]' : 'bg-white/10 text-white/85'
              }`}
            >
              All
            </button>
            {stayFilters.map((a) => (
              <button
                key={a.key}
                type="button"
                onClick={() => setStayFilter(a.key)}
                className={`rounded-full px-4 py-1.5 text-sm capitalize ${
                  stayFilter === a.key ? 'bg-[#c4a35a] text-[#1c2e28]' : 'bg-white/10 text-white/85'
                }`}
              >
                {a.name}
              </button>
            ))}
          </div>

          <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {stays.map((a) => (
              <article key={a.key} className="group overflow-hidden bg-[#1f4339]">
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={a.image}
                    alt={a.name}
                    className="h-full w-full object-cover transition duration-700 group-hover:scale-105"
                  />
                </div>
                <div className="p-5">
                  <h3
                    className="text-2xl"
                    style={{ fontFamily: 'var(--font-turag-display), serif' }}
                  >
                    {a.name}
                  </h3>
                  <p className="mt-2 text-sm text-emerald-50/75">{a.blurb}</p>
                  {'rate' in a && a.rate != null && (
                    <p className="mt-2 text-sm text-[#c4a35a]">From {formatMoney(a.rate, { digits: 0 })} / night</p>
                  )}
                  {book && (
                    <Link
                      href={`${basePath}/book${'rate' in a ? `?room_type=${a.key}` : ''}`}
                      className="mt-4 inline-block text-sm font-medium text-[#c4a35a] hover:underline"
                    >
                      {C.copy.ctaReserve}
                    </Link>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Activities */}
      <section id="activities" className="bg-[#f7f4ee]">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-5 sm:py-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-[#5d6f68]">{C.copy.activitiesEyebrow}</p>
            <h2
              className="mt-2 text-3xl font-semibold text-[#16352d] sm:text-5xl"
              style={{ fontFamily: 'var(--font-turag-display), serif' }}
            >
              {C.copy.activitiesTitle}
            </h2>
            <p className="mt-4 text-[#3a4d46]">{C.copy.activitiesIntro}</p>
            <ul className="mt-8 space-y-4">
              {C.activities.map((a) => (
                <li key={a.name} className="border-b border-[#d9d2c4] pb-3">
                  <p className="font-medium text-[#16352d]">{a.name}</p>
                  <p className="text-sm text-[#5d6f68]">{a.text}</p>
                </li>
              ))}
            </ul>
          </div>
          <div className="grid gap-3">
            <img
              src={C.images.nature}
              alt="River view and boating at Turag Waterfront Resort"
              className="h-56 w-full object-cover sm:h-64"
            />
            <img
              src={C.images.dining}
              alt="Restaurant dining at Turag Waterfront Resort"
              className="h-44 w-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* Gallery — real resort photos featured on Facebook / the official site */}
      <section id="gallery" className="bg-[#f3f0e8]">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-5 sm:py-20">
          <p className="text-xs uppercase tracking-[0.28em] text-[#5d6f68]">{C.copy.galleryEyebrow}</p>
          <h2
            className="mt-2 text-3xl font-semibold text-[#16352d] sm:text-5xl"
            style={{ fontFamily: 'var(--font-turag-display), serif' }}
          >
            {C.copy.galleryTitle}
          </h2>
          <p className="mt-4 max-w-2xl text-[#3a4d46]">{C.copy.galleryIntro}</p>
          <div className="mt-8 flex flex-wrap gap-2">
            {galleryTypes.map((t) => {
              const key = t === 'All' ? 'all' : t
              return (
                <button
                  key={t}
                  type="button"
                  onClick={() => setGalleryFilter(key)}
                  className={`rounded-full px-4 py-1.5 text-sm ${
                    galleryFilter === key ? 'bg-[#16352d] text-white' : 'bg-white text-[#16352d]'
                  }`}
                >
                  {t}
                </button>
              )
            })}
          </div>
          <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {galleryItems.map((g) => (
              <figure key={g.src} className="overflow-hidden bg-white">
                <img src={g.src} alt={g.alt} className="h-56 w-full object-cover sm:h-64" />
              </figure>
            ))}
          </div>
        </div>
      </section>

      {/* Blog */}
      <section id="blog" className="bg-[#f7f4ee]">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-5 sm:py-20">
          <p className="text-xs uppercase tracking-[0.28em] text-[#5d6f68]">{C.copy.blogEyebrow}</p>
          <h2
            className="mt-2 text-3xl font-semibold text-[#16352d] sm:text-5xl"
            style={{ fontFamily: 'var(--font-turag-display), serif' }}
          >
            {C.copy.blogTitle}
          </h2>
          <div className="mt-10 grid gap-6 md:grid-cols-2">
            {(C.blog || []).map((post) => (
              <article key={post.slug} className="border border-[#e4ddd0] bg-white p-6">
                <p className="text-xs uppercase tracking-widest text-[#5d6f68]">{post.date}</p>
                <h3
                  className="mt-2 text-2xl text-[#16352d]"
                  style={{ fontFamily: 'var(--font-turag-display), serif' }}
                >
                  {post.title}
                </h3>
                <p className="mt-2 text-sm text-[#3a4d46]">{post.excerpt}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Gazipur Venue */}
      <section id="venue" className="bg-[#16352d] text-white">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-5 sm:py-20">
          <p className="text-xs uppercase tracking-[0.28em] text-emerald-200/70">{C.copy.venueEyebrow}</p>
          <h2
            className="mt-2 text-3xl font-semibold sm:text-5xl"
            style={{ fontFamily: 'var(--font-turag-display), serif' }}
          >
            {C.copy.venueTitle}
          </h2>
          <p className="mt-4 max-w-2xl text-emerald-50/80">{C.contact.resortAddress}</p>
          <p className="mt-2 max-w-2xl text-sm text-emerald-50/70">Dhaka office: {C.contact.dhakaOffice}</p>
          {book && (
            <Link
              href={`${basePath}/book`}
              className="mt-6 inline-flex min-h-[44px] items-center rounded-full bg-[#c4a35a] px-5 py-2 text-sm font-medium text-[#1c2e28]"
            >
              {C.copy.ctaBook}
            </Link>
          )}
        </div>
      </section>

      {/* Contact / footer */}
      <section id="contact" className="bg-[#0f241f] text-emerald-50">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-5 sm:py-16 md:grid-cols-3">
          <div className="md:col-span-1">
            <span className="inline-flex rounded-2xl bg-[#f7f4ee] px-3 py-2 shadow-md">
              <TuragLogo heightClass="h-20 sm:h-24" src={C.images.logo} />
            </span>
            <p className="mt-3 text-sm text-emerald-100/70">{C.tagline}</p>
            <a
              href={C.contact.facebook}
              target="_blank"
              rel="noreferrer"
              className="mt-3 inline-block text-sm text-[#c4a35a] hover:underline"
            >
              {C.copy.facebook}
            </a>
            <div className="mt-6 flex flex-wrap gap-2">
              {book && (
                <Link
                  href={`${basePath}/book`}
                  className="inline-flex min-h-[44px] items-center rounded-full bg-[#c4a35a] px-4 py-2 text-sm font-medium text-[#1c2e28]"
                >
                  {C.copy.ctaBook}
                </Link>
              )}
              {order && (
                <Link
                  href={`${basePath}/order`}
                  className="inline-flex min-h-[44px] items-center rounded-full border border-white/25 px-4 py-2 text-sm"
                >
                  {C.copy.ctaOrder}
                </Link>
              )}
              <Link href={`/login?site=${subdomain}`} className="inline-flex min-h-[44px] items-center rounded-full px-4 py-2 text-sm text-emerald-100/60 hover:text-white">
                {C.copy.staffLogin}
              </Link>
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-emerald-200/60">Information</p>
            <p className="mt-3 text-sm leading-relaxed text-emerald-50/85">{C.contact.resortAddress}</p>
            <p className="mt-2 text-sm leading-relaxed text-emerald-50/70">{C.contact.dhakaOffice}</p>
            <div className="mt-4 space-y-1 text-sm">
              {C.contact.emails.map((e) => (
                <a key={e} href={`mailto:${e}`} className="block hover:text-[#c4a35a]">
                  {e}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-emerald-200/60">Call us</p>
            <div className="mt-3 space-y-1 text-sm">
              {C.contact.phones.map((p) => (
                <a key={p} href={`tel:${p.replace(/\s/g, '')}`} className="block hover:text-[#c4a35a]">
                  {p}
                </a>
              ))}
            </div>
            <p className="mt-6 text-xs uppercase tracking-[0.22em] text-emerald-200/60">Quick links</p>
            <div className="mt-2 flex flex-wrap gap-3 text-sm">
              {C.nav.map((n) => (
                <a key={n.id} href={`#${n.id}`} className="text-emerald-50/80 hover:text-white">
                  {n.label}
                </a>
              ))}
            </div>
          </div>
        </div>
        <div className="mx-auto max-w-6xl px-4 pb-12 sm:px-5">
          <form onSubmit={submitContact} className="grid gap-3 rounded-lg border border-white/10 bg-white/5 p-5 md:grid-cols-2">
            <p className="md:col-span-2 text-sm font-medium text-white">{C.copy.contactFormTitle}</p>
            <input
              required
              placeholder="Name"
              value={contactForm.name}
              onChange={(e) => setContactForm((f) => ({ ...f, name: e.target.value }))}
              className="min-h-[44px] rounded-md border border-white/15 bg-white/10 px-3 text-sm text-white placeholder:text-emerald-100/40"
            />
            <input
              required
              type="email"
              placeholder="Email"
              value={contactForm.email}
              onChange={(e) => setContactForm((f) => ({ ...f, email: e.target.value }))}
              className="min-h-[44px] rounded-md border border-white/15 bg-white/10 px-3 text-sm text-white placeholder:text-emerald-100/40"
            />
            <input
              placeholder="Phone"
              value={contactForm.phone}
              onChange={(e) => setContactForm((f) => ({ ...f, phone: e.target.value }))}
              className="min-h-[44px] rounded-md border border-white/15 bg-white/10 px-3 text-sm text-white placeholder:text-emerald-100/40"
            />
            <textarea
              required
              placeholder="Message"
              value={contactForm.message}
              onChange={(e) => setContactForm((f) => ({ ...f, message: e.target.value }))}
              className="min-h-[88px] rounded-md border border-white/15 bg-white/10 px-3 py-2 text-sm text-white placeholder:text-emerald-100/40 md:col-span-2"
            />
            <div className="flex items-center gap-3 md:col-span-2">
              <button
                type="submit"
                className="inline-flex min-h-[44px] items-center rounded-full bg-[#c4a35a] px-5 text-sm font-medium text-[#1c2e28]"
              >
                Send
              </button>
              {contactStatus && <p className="text-sm text-emerald-100/80">{contactStatus}</p>}
            </div>
          </form>
        </div>
        <div className="border-t border-white/10 px-5 py-5 text-center text-xs text-emerald-100/40">
          © {new Date().getFullYear()} {C.brand}. {C.copy.footerNote} · Guest portal for{' '}
          {subdomain}
        </div>
      </section>
    </div>
  )
}
