import type { Metadata } from 'next'
import { fetchPublicLanding } from '@/lib/public-landing'

export async function generateMetadata({ params }: { params: { subdomain: string } }): Promise<Metadata> {
  const tenant = await fetchPublicLanding(params.subdomain)
  const name = tenant?.name || 'Resort'
  return {
    title: `Order dining | ${name}`,
    description: `Order food from ${name}.`,
    robots: { index: true, follow: true },
  }
}

export default function OrderLayout({ children }: { children: React.ReactNode }) {
  return children
}
