import type { Metadata } from 'next'
import { fetchPublicLanding } from '@/lib/public-landing'

export async function generateMetadata({ params }: { params: { subdomain: string } }): Promise<Metadata> {
  const tenant = await fetchPublicLanding(params.subdomain)
  const name = tenant?.name || 'Resort'
  return {
    title: `Book a stay | ${name}`,
    description: `Request a reservation at ${name}.`,
    robots: { index: true, follow: true },
  }
}

export default function BookLayout({ children }: { children: React.ReactNode }) {
  return children
}
