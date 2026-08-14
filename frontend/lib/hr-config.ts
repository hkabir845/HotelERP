import type { MasterDef } from '@/lib/frontdesk-config'

const yesNo = [{ key: 'is_active', label: 'Active', type: 'checkbox' as const }]

export const HR_MASTERS: Record<string, MasterDef> = {
  employees: {
    kind: 'employees',
    title: 'Employees',
    subtitle: 'Staff master used by punch, leave, loans, salary structure, and payroll.',
    fields: [
      { key: 'first_name', label: 'First name', required: true },
      { key: 'last_name', label: 'Last name', required: true },
      { key: 'phone', label: 'Phone' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'branch', label: 'Branch', type: 'select', optionsKey: 'branches', optionValue: 'name' },
      { key: 'department', label: 'Department', type: 'select', optionsKey: 'departments', optionValue: 'name' },
      { key: 'designation', label: 'Designation', type: 'select', optionsKey: 'designations', optionValue: 'name' },
      { key: 'work_shift', label: 'Work shift', type: 'select', optionsKey: 'work_shifts', optionValue: 'name' },
      { key: 'salary', label: 'Salary', type: 'number' },
      { key: 'hire_date', label: 'Hire date', type: 'date' },
      { key: 'status', label: 'Status', type: 'select', optionsKey: 'employment_statuses' },
      { key: 'bank_name', label: 'Bank' },
      { key: 'bank_account', label: 'Account no.' },
      { key: 'notes', label: 'Notes', type: 'textarea' },
    ],
    columns: [
      { key: 'employee_number', label: 'Number' },
      { key: 'name', label: 'Name' },
      { key: 'department', label: 'Department' },
      { key: 'designation', label: 'Designation' },
      { key: 'work_shift', label: 'Shift' },
      { key: 'salary', label: 'Salary' },
      { key: 'status', label: 'Status' },
    ],
  },
  branches: {
    kind: 'branches',
    title: 'Branches',
    subtitle: 'Properties / branches assigned to employees.',
    fields: [
      { key: 'name', label: 'Branch', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Branch' },
      { key: 'description', label: 'Notes' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  departments: {
    kind: 'departments',
    title: 'Departments',
    subtitle: 'Departments on the employee master and payroll.',
    fields: [
      { key: 'name', label: 'Department', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Department' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  designations: {
    kind: 'designations',
    title: 'Designations',
    subtitle: 'Job titles assigned to employees.',
    fields: [
      { key: 'name', label: 'Designation', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Designation' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'work-shifts': {
    kind: 'work-shifts',
    title: 'Work Shifts',
    subtitle: 'Shift start/end used to flag late punch-ins.',
    fields: [
      { key: 'name', label: 'Shift', required: true },
      { key: 'start_time', label: 'Start (HH:MM)', placeholder: '09:00' },
      { key: 'end_time', label: 'End (HH:MM)', placeholder: '17:00' },
      { key: 'grace_minutes', label: 'Grace minutes', type: 'number' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Shift' },
      { key: 'start_time', label: 'Start' },
      { key: 'end_time', label: 'End' },
      { key: 'grace_minutes', label: 'Grace' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'leave-types': {
    kind: 'leave-types',
    title: 'Leave Management',
    subtitle: 'Leave types and yearly entitlement used on leave requests.',
    fields: [
      { key: 'name', label: 'Leave type', required: true },
      { key: 'days_per_year', label: 'Days / year', type: 'number' },
      { key: 'is_paid', label: 'Paid', type: 'checkbox' },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'name', label: 'Type' },
      { key: 'days_per_year', label: 'Days / year' },
      { key: 'is_paid', label: 'Paid' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  holidays: {
    kind: 'holidays',
    title: 'Public Holidays',
    subtitle: 'Holiday calendar for the property.',
    fields: [
      { key: 'name', label: 'Holiday', required: true },
      { key: 'holiday_date', label: 'Date', type: 'date', required: true },
      { key: 'description', label: 'Notes', type: 'textarea' },
      ...yesNo,
    ],
    columns: [
      { key: 'holiday_date', label: 'Date' },
      { key: 'name', label: 'Holiday' },
      { key: 'is_active', label: 'Active' },
    ],
  },
  'salary-structures': {
    kind: 'salary-structures',
    title: 'Salary Structure',
    subtitle: 'Per-employee basic and allowances used when generating payroll.',
    fields: [
      { key: 'employee_id', label: 'Employee', type: 'select', optionsKey: 'employees', required: true },
      { key: 'basic', label: 'Basic', type: 'number', required: true },
      { key: 'house_rent', label: 'House rent', type: 'number' },
      { key: 'medical', label: 'Medical', type: 'number' },
      { key: 'conveyance', label: 'Conveyance', type: 'number' },
      { key: 'other_allowance', label: 'Other', type: 'number' },
      { key: 'tax_percent', label: 'Tax %', type: 'number' },
    ],
    columns: [
      { key: 'employee_name', label: 'Employee' },
      { key: 'basic', label: 'Basic' },
      { key: 'house_rent', label: 'HRA' },
      { key: 'medical', label: 'Medical' },
      { key: 'conveyance', label: 'Conveyance' },
      { key: 'tax_percent', label: 'Tax %' },
      { key: 'gross', label: 'Gross' },
    ],
  },
}

export const HR_ENDPOINT = '/hr/config'
