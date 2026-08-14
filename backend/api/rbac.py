"""
Hotel ERP RBAC — roles mapped to least-privilege modules and capabilities.

Designed around global PMS practice (Opera / Mews / Cloudbeds patterns):
- Roles = stable job functions, not one-off titles
- Tenant modules ∩ role modules = effective access
- Separation of duties: Purchase Officer cannot post GL vouchers;
  Accountant owns ledgers; Front Desk owns guest folio ops
"""
from __future__ import annotations

from typing import Any

# Capability flags used by UI + future API guards
CAP_VIEW_DASHBOARD = 'dashboard.view'
CAP_MANAGE_USERS = 'users.manage'
CAP_POST_VOUCHERS = 'accounts.post_vouchers'
CAP_MANAGE_COA = 'accounts.manage_coa'
CAP_VIEW_FINANCE = 'accounts.view_reports'
CAP_PURCHASE = 'inventory.purchase'
CAP_APPROVE_PO = 'inventory.approve_po'
CAP_POS = 'fnb.pos'
CAP_CHECKIN = 'frontdesk.checkin'
CAP_FOLIO = 'frontdesk.folio'
CAP_ROOM_STATUS = 'housekeeping.room_status'
CAP_HK_TASKS = 'housekeeping.tasks'

ALL_MODULE_KEYS = [
    'frontdesk',
    'housekeeping',
    'fnb',
    'recipes',
    'laundry',
    'spa',
    'hall',
    'banquet',
    'pool',
    'crm',
    'accounts',
    'inventory',
    'assets',
    'broadcast',
    'hr',
    'channel',
    'reports',
    'utilities',
    'landing',
]

# Menu section titles (must match gyoroom-menu top-level titles)
ROLE_DEFINITIONS: dict[str, dict[str, Any]] = {
    'superadmin': {
        'label': 'Platform Superadmin',
        'description': 'SaaS control plane — tenants, billing, catalog.',
        'home_path': '/saas',
        'modules': list(ALL_MODULE_KEYS),
        'menu_sections': None,  # all
        'capabilities': [CAP_MANAGE_USERS, CAP_VIEW_DASHBOARD],
        'color': '#6366f1',
    },
    'admin': {
        'label': 'Property Administrator',
        'description': 'Full property access including utilities and user management.',
        'home_path': '/home',
        'modules': list(ALL_MODULE_KEYS),
        'menu_sections': None,
        'capabilities': [
            CAP_VIEW_DASHBOARD,
            CAP_MANAGE_USERS,
            CAP_POST_VOUCHERS,
            CAP_MANAGE_COA,
            CAP_VIEW_FINANCE,
            CAP_PURCHASE,
            CAP_APPROVE_PO,
            CAP_POS,
            CAP_CHECKIN,
            CAP_FOLIO,
            CAP_ROOM_STATUS,
            CAP_HK_TASKS,
        ],
        'color': '#0f766e',
    },
    'operations_manager': {
        'label': 'Operations Manager',
        'description': 'Cross-department ops: rooms, F&B, inventory, assets, CRM, reports. No user admin.',
        'home_path': '/home/operations',
        'modules': [
            'frontdesk',
            'housekeeping',
            'fnb',
            'recipes',
            'laundry',
            'spa',
            'hall',
            'banquet',
            'pool',
            'crm',
            'inventory',
            'assets',
            'broadcast',
            'reports',
            'channel',
        ],
        'menu_sections': [
            'Dashboard',
            'FRONTDESK',
            'HOUSEKEEPING',
            'BANQUET',
            'F&B AND REVENUE CENTER',
            'INVENTORY',
            'SALES & MARKETING',
            'ASSET & MAINTANANCE',
            'ASSET & MAINTENANCE',
            'BROADCAST MESSAGE',
            'CHANNEL MANAGER',
            'REPORT CENTER',
        ],
        'capabilities': [
            CAP_VIEW_DASHBOARD,
            CAP_PURCHASE,
            CAP_APPROVE_PO,
            CAP_POS,
            CAP_CHECKIN,
            CAP_FOLIO,
            CAP_ROOM_STATUS,
            CAP_HK_TASKS,
            CAP_VIEW_FINANCE,
        ],
        'color': '#1d4ed8',
    },
    'manager': {
        # Alias kept for legacy users — same as operations_manager
        'label': 'Manager',
        'description': 'Property operations oversight (legacy alias of Operations Manager).',
        'home_path': '/home/operations',
        'modules': None,  # copy from operations_manager at resolve time
        'alias_of': 'operations_manager',
        'color': '#1d4ed8',
    },
    'frontdesk': {
        'label': 'Front Desk',
        'description': 'Reservations, arrivals/departures, folio, room rack, guest CRM.',
        'home_path': '/home/frontdesk',
        'modules': ['frontdesk', 'housekeeping', 'crm', 'broadcast', 'reports', 'channel'],
        'menu_sections': [
            'Dashboard',
            'FRONTDESK',
            'HOUSEKEEPING',
            'SALES & MARKETING',
            'BROADCAST MESSAGE',
            'CHANNEL MANAGER',
            'REPORT CENTER',
        ],
        'capabilities': [
            CAP_VIEW_DASHBOARD,
            CAP_CHECKIN,
            CAP_FOLIO,
            CAP_ROOM_STATUS,
        ],
        'color': '#2563eb',
    },
    'housekeeping': {
        'label': 'Housekeeping',
        'description': 'Room status board, HK tasks, lost & found, amenity, laundry.',
        'home_path': '/home/housekeeping',
        'modules': ['housekeeping', 'laundry', 'assets', 'reports'],
        'menu_sections': [
            'Dashboard',
            'HOUSEKEEPING',
            'LAUNDRY',
            'ASSET & MAINTANANCE',
            'ASSET & MAINTENANCE',
            'REPORT CENTER',
        ],
        'capabilities': [CAP_VIEW_DASHBOARD, CAP_ROOM_STATUS, CAP_HK_TASKS],
        'color': '#059669',
    },
    'restaurant': {
        'label': 'Restaurant / F&B',
        'description': 'POS, orders, menu, revenue centers, recipes, kitchen stock.',
        'home_path': '/home/restaurant',
        'modules': ['fnb', 'recipes', 'inventory', 'reports'],
        'menu_sections': [
            'Dashboard',
            'F&B AND REVENUE CENTER',
            'FOOD & BEVERAGE',
            'RECIPE MANAGEMENT',
            'INVENTORY',
            'REPORT CENTER',
        ],
        'capabilities': [CAP_VIEW_DASHBOARD, CAP_POS],
        'color': '#c2410c',
    },
    'fnb': {
        'label': 'F&B',
        'description': 'Legacy F&B role — same access as Restaurant.',
        'home_path': '/home/restaurant',
        'alias_of': 'restaurant',
        'color': '#c2410c',
    },
    'accountant': {
        'label': 'Accountant',
        'description': 'Chart of accounts, vouchers, ledgers, financial reports. No purchasing.',
        'home_path': '/home/accountant',
        'modules': ['accounts', 'reports'],
        'menu_sections': ['Dashboard', 'ACCOUNTS', 'REPORT CENTER'],
        'capabilities': [
            CAP_VIEW_DASHBOARD,
            CAP_POST_VOUCHERS,
            CAP_MANAGE_COA,
            CAP_VIEW_FINANCE,
        ],
        'color': '#7c3aed',
        'account_permissions': {
            'can_post_vouchers': True,
            'can_view_reports': True,
            'can_manage_coa': True,
        },
    },
    'purchase_officer': {
        'label': 'Purchase Officer',
        'description': 'Purchase orders, suppliers, stock receipts. Cannot post GL vouchers (SoD).',
        'home_path': '/home/purchase',
        'modules': ['inventory', 'reports'],
        'menu_sections': ['Dashboard', 'INVENTORY', 'REPORT CENTER'],
        'capabilities': [CAP_VIEW_DASHBOARD, CAP_PURCHASE],
        'color': '#b45309',
        'account_permissions': {
            'can_post_vouchers': False,
            'can_view_reports': True,
            'can_manage_coa': False,
        },
    },
    'maintenance': {
        'label': 'Maintenance',
        'description': 'Assets, work orders, room out-of-order coordination.',
        'home_path': '/home/housekeeping',
        'modules': ['assets', 'housekeeping', 'reports'],
        'menu_sections': [
            'Dashboard',
            'HOUSEKEEPING',
            'ASSET & MAINTANANCE',
            'ASSET & MAINTENANCE',
            'REPORT CENTER',
        ],
        'capabilities': [CAP_VIEW_DASHBOARD, CAP_ROOM_STATUS],
        'color': '#64748b',
    },
    'staff': {
        'label': 'Staff',
        'description': 'Minimal dashboard access until assigned a department role.',
        'home_path': '/home',
        'modules': [],
        'menu_sections': ['Dashboard'],
        'capabilities': [CAP_VIEW_DASHBOARD],
        'color': '#6b7280',
    },
}


def resolve_role(role: str | None) -> dict[str, Any]:
    key = (role or 'staff').lower().strip()
    base = ROLE_DEFINITIONS.get(key) or ROLE_DEFINITIONS['staff']
    if base.get('alias_of'):
        parent = ROLE_DEFINITIONS[base['alias_of']]
        merged = {**parent, **{k: v for k, v in base.items() if k not in ('alias_of', 'modules', 'menu_sections', 'capabilities')}}
        merged['modules'] = parent.get('modules')
        merged['menu_sections'] = parent.get('menu_sections')
        merged['capabilities'] = parent.get('capabilities')
        merged['key'] = key
        return merged
    out = dict(base)
    out['key'] = key
    return out


def effective_modules(role: str | None, tenant_modules: list[str] | None, *, is_superuser: bool = False) -> list[str]:
    if is_superuser:
        return list(ALL_MODULE_KEYS)
    role_def = resolve_role(role)
    role_mods = role_def.get('modules')
    if role_mods is None:
        role_mods = list(ALL_MODULE_KEYS)
    tenant = list(tenant_modules or [])
    if not tenant:
        # Empty tenant list historically means "all enabled" in this ERP
        return list(role_mods)
    if role_def['key'] in ('admin', 'superadmin'):
        return [m for m in tenant if m in ALL_MODULE_KEYS] or list(tenant)
    allowed = set(role_mods)
    return [m for m in tenant if m in allowed]


def role_allows_section(role: str | None, section_title: str, *, is_superuser: bool = False) -> bool:
    if is_superuser:
        return True
    role_def = resolve_role(role)
    if role_def['key'] in ('admin', 'superadmin'):
        return True
    sections = role_def.get('menu_sections')
    if sections is None:
        return True
    if not sections:
        return section_title == 'Dashboard'
    return section_title in sections or section_title.upper() in {s.upper() for s in sections}


def has_capability(role: str | None, capability: str, *, is_superuser: bool = False) -> bool:
    if is_superuser:
        return True
    role_def = resolve_role(role)
    if role_def['key'] == 'admin':
        return True
    return capability in (role_def.get('capabilities') or [])


def serialize_rbac(user) -> dict[str, Any]:
    role = getattr(user, 'role', None) or 'staff'
    is_super = bool(getattr(user, 'is_superuser', False))
    tenant = getattr(user, 'tenant', None)
    tenant_mods = tenant.get_enabled_modules() if tenant is not None else []
    role_def = resolve_role(role)
    modules = effective_modules(role, tenant_mods, is_superuser=is_super)
    return {
        'role': role_def['key'],
        'role_label': role_def.get('label') or role,
        'role_description': role_def.get('description') or '',
        'home_path': '/saas' if is_super else (role_def.get('home_path') or '/home'),
        'modules': modules,
        'menu_sections': role_def.get('menu_sections'),
        'capabilities': list(role_def.get('capabilities') or []) if not is_super and role_def['key'] != 'admin' else [
            CAP_VIEW_DASHBOARD,
            CAP_MANAGE_USERS,
            CAP_POST_VOUCHERS,
            CAP_MANAGE_COA,
            CAP_VIEW_FINANCE,
            CAP_PURCHASE,
            CAP_APPROVE_PO,
            CAP_POS,
            CAP_CHECKIN,
            CAP_FOLIO,
            CAP_ROOM_STATUS,
            CAP_HK_TASKS,
        ],
        'color': role_def.get('color') or '#6b7280',
    }


def list_operational_roles() -> list[dict[str, Any]]:
    """Roles shown in login demos / utilities (exclude aliases & superadmin)."""
    keys = [
        'admin',
        'operations_manager',
        'frontdesk',
        'housekeeping',
        'restaurant',
        'accountant',
        'purchase_officer',
    ]
    out = []
    for key in keys:
        d = resolve_role(key)
        out.append({
            'key': key,
            'label': d['label'],
            'description': d['description'],
            'home_path': d['home_path'],
            'color': d.get('color'),
        })
    return out
