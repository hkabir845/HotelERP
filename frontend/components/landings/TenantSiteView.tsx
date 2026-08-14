'use client'

import { useMemo } from 'react'
import TuragLanding from '@/components/landings/TuragLanding'
import HospitalitySite from '@/components/landings/HospitalitySite'
import type { LandingContent } from '@/lib/landings/turag-content'
import type { PublicLanding } from '@/lib/public-landing'
import { publicSiteBasePath } from '@/lib/public-landing'

export default function TenantSiteView({
  tenant,
  content,
  subdomain,
}: {
  tenant: PublicLanding
  content: LandingContent
  subdomain: string
}) {
  const sub = (tenant.subdomain || subdomain || '').toLowerCase()
  const template = (tenant.landing_template || tenant.product_type || 'hotel').toLowerCase()

  const basePath = useMemo(() => {
    const host = typeof window !== 'undefined' ? window.location.hostname : ''
    return publicSiteBasePath(sub, { domain: tenant.domain, host })
  }, [sub, tenant.domain])

  if (template === 'turag' || sub === 'turag') {
    return (
      <TuragLanding
        subdomain={sub}
        basePath={basePath}
        ctas={tenant.ctas}
        subscriptionActive={tenant.subscription_active !== false}
        content={content}
        roomTypes={tenant.room_types}
        menuItems={tenant.menu}
      />
    )
  }

  return <HospitalitySite tenant={tenant} subdomain={sub} basePath={basePath} />
}
