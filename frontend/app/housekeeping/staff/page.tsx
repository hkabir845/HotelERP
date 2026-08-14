'use client'

import ConfigMasterPage from '@/components/ConfigMasterPage'
import { HR_ENDPOINT, HR_MASTERS } from '@/lib/hr-config'

/** Same Employee master as HR → Employees, filtered to Housekeeping. */
export default function HousekeepingStaffPage() {
  return (
    <ConfigMasterPage
      kind="employees"
      catalog={HR_MASTERS}
      endpoint={HR_ENDPOINT}
      queryParams={{ department: 'Housekeeping' }}
      defaults={{ department: 'Housekeeping', status: 'active' }}
      titleOverride="Housekeeping Staff"
      subtitleOverride="Same Employee master as HR — showing Housekeeping department only."
    />
  )
}
