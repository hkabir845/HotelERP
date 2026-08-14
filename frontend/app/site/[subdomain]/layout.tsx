import type { Metadata, Viewport } from 'next'
import { fetchPublicLanding, metadataForLanding } from '@/lib/public-landing'

type Props = { params: { subdomain: string }; children: React.ReactNode }

export async function generateMetadata({ params }: { params: { subdomain: string } }): Promise<Metadata> {
  const tenant = await fetchPublicLanding(params.subdomain)
  if (!tenant) {
    return { title: 'Page not found', robots: { index: false, follow: false } }
  }
  return metadataForLanding(tenant, params.subdomain)
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0f241f',
}

export default function SiteLayout({ children }: Props) {
  return children
}
