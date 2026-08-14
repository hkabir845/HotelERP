'use client'

import { useEffect, useState } from 'react'

export type HeroSlide = { src: string; alt: string }

type Props = {
  slides: HeroSlide[]
  className?: string
  /** How long each photo stays on screen before the next one */
  holdMs?: number
}

const HOLD_MS = 5500
const SLIDE_MS = 800

export default function TuragHeroSlideshow({
  slides,
  className = '',
  holdMs = HOLD_MS,
}: Props) {
  const items = slides.filter((s) => s?.src)
  const n = items.length
  const track = n > 1 ? [...items, items[0]] : items

  const [index, setIndex] = useState(0)
  const [animate, setAnimate] = useState(true)

  useEffect(() => {
    if (n < 2 || index >= n) return
    const id = window.setTimeout(() => {
      setAnimate(true)
      setIndex((i) => i + 1)
    }, holdMs)
    return () => window.clearTimeout(id)
  }, [n, holdMs, index])

  const onTransitionEnd = () => {
    if (n < 2) return
    if (index >= n) {
      setAnimate(false)
      setIndex(0)
    }
  }

  if (!items.length) return null

  return (
    <div
      className={`relative w-full overflow-hidden bg-[#0f241f] ${className}`}
      role="region"
      aria-roledescription="carousel"
      aria-label="Resort photos"
      aria-live="off"
    >
      <div
        className="flex h-full"
        style={{
          transform: `translate3d(-${index * 100}%, 0, 0)`,
          transition: animate ? `transform ${SLIDE_MS}ms ease-in-out` : 'none',
        }}
        onTransitionEnd={onTransitionEnd}
      >
        {track.map((slide, i) => (
          <img
            key={`${slide.src}-${i}`}
            src={slide.src}
            alt={i === index || (index >= n && i === 0) ? slide.alt : ''}
            aria-hidden={!(i === index || (index >= n && i === 0))}
            draggable={false}
            className="h-full min-w-full max-w-none shrink-0 basis-full object-cover object-bottom"
          />
        ))}
      </div>
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#0a1a16]/55 via-[#0a1a16]/15 to-transparent" />
    </div>
  )
}
