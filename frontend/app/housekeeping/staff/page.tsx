'use client'

import ConfigMasterPage from '@/components/ConfigMasterPage'
import { HR_ENDPOINT, HR_MASTERS } from '@/lib/hr-config'

/** Same Employee master as HR → Employees, filtered to Housekeeping (add only from HR). */
export default function HousekeepingStaffPage() {
  return (
    <ConfigMasterPage
      kind="employees"
      catalog={HR_MASTERS}
      endpoint={HR_ENDPOINT}
      queryParams={{ department: 'Housekeeping' }}
      defaults={{ department: 'Housekeeping', status: 'active' }}
      allowCreate={false}
      titleOverride="Housekeeping Staff"
      subtitleOverride="Employees in the Housekeeping department. Add new people under HR → Employees."
    />
  )
}
