'use client'
import FnbReportPage from '@/components/FnbReportPage'

export default function FrontdeskReportPage({
  kind,
  title,
  subtitle,
  hideDates,
}: {
  kind: string
  title: string
  subtitle: string
  hideDates?: boolean
}) {
  return (
    <FnbReportPage
      endpoint="/frontdesk/reports"
      kind={kind}
      title={title}
      subtitle={subtitle}
      hideDates={hideDates}
    />
  )
}
