'use client'
import RecordWorkbench from '@/components/RecordWorkbench'
export default function Page() {
  return (
    <RecordWorkbench
      title="User-Wise Accounts Config"
      subtitle="Which users may post vouchers, view accounts reports, or manage the chart of accounts."
      endpoint="/utilities/account-permissions"
      createLabel="Save permissions"
      fields={[
        { key: 'user_id', label: 'User', type: 'select', optionsKey: 'users', required: true },
        { key: 'can_post_vouchers', label: 'Post vouchers', type: 'checkbox' },
        { key: 'can_view_reports', label: 'View reports', type: 'checkbox' },
        { key: 'can_manage_coa', label: 'Manage chart of accounts', type: 'checkbox' },
      ]}
      columns={[
        { key: 'name', label: 'User' },
        { key: 'username', label: 'Login' },
        { key: 'role', label: 'Role' },
        { key: 'can_post_vouchers', label: 'Vouchers' },
        { key: 'can_view_reports', label: 'Reports' },
        { key: 'can_manage_coa', label: 'COA' },
      ]}
    />
  )
}
