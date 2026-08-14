'use client'

import Link from 'next/link'
import { TURAG_CONTENT } from '@/lib/landings/turag-content'

type Props = {
  href?: string
  className?: string
  /** Height class for the logo image */
  heightClass?: string
  /** Show brand text next to logo (compact ERP sidebar) */
  showWordmark?: boolean
  /** Soft light plate so the logo stays readable on dark backgrounds */
  onDark?: boolean
  priority?: boolean
  src?: string
}

/** Official Turag Waterfront Resort logo mark. */
export default function TuragLogo({
  href,
  className = '',
  heightClass = 'h-16',
  showWordmark = false,
  onDark = false,
  src,
}: Props) {
  const img = (
    <img
      src={src || TURAG_CONTENT.images.logo}
      alt="Turag Waterfront Resort — A Resort by Nature"
      className={`${heightClass} w-auto max-w-[320px] object-contain ${className}`}
    />
  )

  const inner = showWordmark ? (
    <span className="inline-flex items-center gap-2">{img}</span>
  ) : (
    img
  )

  const content = (
    <span
      className={`inline-flex items-center ${onDark ? 'turag-logo-on-photo' : ''}`}
    >
      {inner}
    </span>
  )

  if (href) {
    const isHash = href.startsWith('#')
    if (isHash) {
      return (
        <a href={href} className="inline-flex shrink-0 items-center" aria-label="Turag Waterfront Resort">
          {content}
        </a>
      )
    }
    return (
      <Link href={href} className="inline-flex shrink-0 items-center" aria-label="Turag Waterfront Resort">
        {content}
      </Link>
    )
  }

  return <span className="inline-flex shrink-0 items-center">{content}</span>
}

export function TuragPublicHeader({
  subdomain,
  basePath,
  right,
}: {
  subdomain: string
  basePath?: string
  right?: React.ReactNode
}) {
  const home = basePath ?? `/site/${subdomain}`
  return (
    <header className="border-b border-[#d9d2c4] bg-[#f3f0e8]/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <TuragLogo href={home || '/'} heightClass="h-20 sm:h-24" />
        <div className="flex items-center gap-3">{right}</div>
      </div>
    </header>
  )
}
