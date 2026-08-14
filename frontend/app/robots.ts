import type { MetadataRoute } from 'next'
import { siteOrigin } from '@/lib/public-landing'

export default function robots(): MetadataRoute.Robots {
  const origin = siteOrigin()
  return {
    rules: [
      {
        userAgent: '*',
        allow: ['/', '/site/'],
        disallow: [
          '/login',
          '/saas',
          '/home',
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
          '/api/',
        ],
      },
    ],
    sitemap: `${origin}/sitemap.xml`,
  }
}
