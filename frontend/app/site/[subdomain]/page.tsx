import Link from 'next/link'
import { fetchPublicLanding, jsonLdForLanding, landingContentFor } from '@/lib/public-landing'
import TenantSiteView from '@/components/landings/TenantSiteView'

export const revalidate = 30

export default async function TenantLandingPage({ params }: { params: { subdomain: string } }) {
  const tenant = await fetchPublicLanding(params.subdomain)
  if (!tenant) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="rounded-xl border bg-white p-8 text-center shadow-sm">
          <h1 className="text-xl font-semibold">Page not found</h1>
          <p className="mt-2 text-sm text-slate-600">This landing page is unavailable.</p>
          <Link href="/login" className="mt-4 inline-block text-indigo-600 hover:underline">
            Staff login
          </Link>
        </div>
      </div>
    )
  }

  const content = landingContentFor(tenant)
  const jsonLd = jsonLdForLanding(tenant, content)

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <TenantSiteView tenant={tenant} content={content} subdomain={params.subdomain} />
    </>
  )
}
