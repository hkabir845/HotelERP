import type { MetadataRoute } from 'next'
import { fetchPublicSites, siteOrigin } from '@/lib/public-landing'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const origin = siteOrigin()
  const sites = await fetchPublicSites()
  const now = new Date()

  const entries: MetadataRoute.Sitemap = [
    {
      url: origin,
      lastModified: now,
      changeFrequency: 'weekly',
      priority: 0.6,
    },
  ]

  for (const site of sites) {
    const lastModified = site.updated_at ? new Date(site.updated_at) : now
    entries.push({
      url: `${origin}/site/${site.subdomain}`,
      lastModified,
      changeFrequency: 'weekly',
      priority: 1,
    })
    entries.push({
      url: `${origin}/site/${site.subdomain}/book`,
      lastModified,
      changeFrequency: 'monthly',
      priority: 0.7,
    })
    entries.push({
      url: `${origin}/site/${site.subdomain}/order`,
      lastModified,
      changeFrequency: 'monthly',
      priority: 0.6,
    })
  }

  return entries
}
