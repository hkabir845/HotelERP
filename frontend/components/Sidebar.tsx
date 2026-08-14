'use client'

import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  Calendar,
  Users,
  Bed,
  UtensilsCrossed,
  Calculator,
  Wrench,
  MessageSquare,
  Settings,
  FileText,
  TrendingUp,
  Package,
  Home,
  LogOut,
  ChevronRight,
  Search,
  BookOpen,
  Leaf,
  Bell,
  PanelLeftOpen,
  ToggleRight,
  ClipboardList,
  Building2,
  DollarSign,
  LayoutGrid,
} from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { useUiStore } from '@/lib/ui-store'
import { SIDEBAR_MODULE_MAP, hasModule, ModuleKey } from '@/lib/modules'
import { getGyoroomMenu, MenuItem } from '@/lib/gyoroom-menu'
import { TURAG_CONTENT } from '@/lib/landings/turag-content'
import { homePathForUser, roleAllowsMenuSection } from '@/lib/rbac'

const SIDEBAR_BG = '#3d4a5c'
const SECTION_BG = '#354155'
const ROW_HOVER = '#475569'
const ROW_ACTIVE = '#e85d3b'
const ROW_ACTIVE_SOFT = 'rgba(232, 93, 59, 0.22)'
const ACCENT = '#e85d3b'

type NavItem = MenuItem & { icon?: ReactNode; children?: NavItem[] }

function iconForTitle(title: string): ReactNode {
  const t = title.toLowerCase()
  const cls = 'h-[18px] w-[18px] shrink-0 stroke-[1.5]'

  if (t === 'dashboard') return <LayoutDashboard className={cls} />
  if (t === 'apps center') return <LayoutGrid className={cls} />
  if (t.includes('booking') || t.includes('reservation') || t.includes('arrival') || t.includes('departure'))
    return <BookOpen className={cls} />
  if (t.includes('inhouse') || t.includes('guest status')) return <Leaf className={cls} />
  if (t.includes('folio') || t.includes('report') || t.includes('forecast') || t.includes('schedule') || t.includes('rack'))
    return <FileText className={cls} />
  if (t.includes('config') || t.includes('setting')) return <Settings className={cls} />
  if (t.includes('agent fund') || t.includes('fund')) return <DollarSign className={cls} />
  if (t.includes('room status') || t.includes('room') || t === 'staff' || t === 'task' || t.includes('lost'))
    return <Home className={cls} />
  if (t.includes('amenity')) return <Package className={cls} />
  if (t.includes('maintenance') || t.includes('block') || t.includes('asset')) return <Wrench className={cls} />
  if (t.includes('wake')) return <Bell className={cls} />
  if (t.includes('event') || t.includes('banquet') || t.includes('venue')) return <Building2 className={cls} />
  if (t.includes('order') || t.includes('pos') || t.includes('sales') || t.includes('f&b') || t.includes('revenue center'))
    return <UtensilsCrossed className={cls} />
  if (t.includes('voucher') || t.includes('account') || t.includes('ledger') || t.includes('loan'))
    return <Calculator className={cls} />
  if (t.includes('inventory') || t.includes('stock') || t.includes('purchase') || t.includes('requisition') || t.includes('warehouse') || t.includes('supplier'))
    return <Package className={cls} />
  if (t.includes('hr') || t.includes('employee') || t.includes('payroll') || t.includes('attendance') || t.includes('human'))
    return <Users className={cls} />
  if (t.includes('sales') || t.includes('marketing') || t.includes('crm')) return <TrendingUp className={cls} />
  if (t.includes('broadcast') || t.includes('message')) return <MessageSquare className={cls} />
  if (t.includes('utilit')) return <Settings className={cls} />
  if (t.includes('housekeep')) return <Bed className={cls} />
  if (t.includes('frontdesk')) return <Calendar className={cls} />
  return <ClipboardList className={cls} />
}

function activeOrSectionIcon(active: boolean, inSection: boolean) {
  if (active) return 'text-white'
  if (inSection) return 'text-orange-200'
  return 'text-slate-200 opacity-90'
}

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout, tenant_subdomain } = useAuthStore()
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen)
  const [expandedMenus, setExpandedMenus] = useState<string[]>([])
  const [query, setQuery] = useState('')
  const menuScrollRef = useRef<HTMLDivElement>(null)
  const enabledModules = (user?.enabled_modules || user?.tenant?.enabled_modules || []) as string[]
  const isSuperuser = !!user?.is_superuser
  const userRole = user?.role
  const dashHome = homePathForUser(user)
  const isTurag =
    (tenant_subdomain || user?.tenant?.subdomain || '').toLowerCase() === 'turag' ||
    (user?.tenant?.name || '').toLowerCase().includes('turag')
  const tenantLogo = user?.tenant?.logo || (isTurag ? TURAG_CONTENT.images.logo : null)
  const tenantName = user?.tenant?.name || (isTurag ? 'Turag Waterfront Resort' : 'Hotel ERP')

  useEffect(() => {
    document.documentElement.classList.toggle('sidebar-hidden', !sidebarOpen)
    return () => document.documentElement.classList.remove('sidebar-hidden')
  }, [sidebarOpen])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const withIcons = (items: MenuItem[]): NavItem[] =>
    items.map((item) => ({
      ...item,
      icon: iconForTitle(item.title),
      children: item.children ? withIcons(item.children) : undefined,
    }))

  const itemId = (item: NavItem, parentId: string) =>
    item.key || item.path || `${parentId}/${item.title}`

  const filterByModule = (items: NavItem[]): NavItem[] => {
    if (isSuperuser) return items
    return items
      .filter((item) => {
        if (item.title === 'Dashboard' || item.title === 'Apps Center') return true
        if (!roleAllowsMenuSection(userRole, item.title, isSuperuser)) return false
        const topKey = SIDEBAR_MODULE_MAP[item.title]
        if (topKey && !hasModule(enabledModules, topKey as ModuleKey)) return false
        if (item.module && !hasModule(enabledModules, item.module)) return false
        return true
      })
      .map((item) => {
        if (item.title === 'Dashboard') {
          return { ...item, path: dashHome || item.path || '/home' }
        }
        return item.children ? { ...item, children: filterByModule(item.children) } : item
      })
      .filter((item) => !item.children || item.children.length > 0 || item.path)
  }

  const wordsOf = (value: string) =>
    value.toLowerCase().split(/[^a-z0-9&]+/).filter(Boolean)

  const wordsMatch = (text: string, needle: string) => {
    const queryWords = wordsOf(needle)
    if (!queryWords.length) return true
    const hayWords = wordsOf(text)
    return queryWords.every((qw) => hayWords.some((hw) => hw.startsWith(qw)))
  }

  const itemMatches = (item: NavItem, needle: string) =>
    wordsMatch(item.title, needle) ||
    (!!item.path && wordsMatch(item.path.replace(/[/_-]+/g, ' '), needle))

  const highlightTitle = (title: string, needle: string) => {
    const queryWords = wordsOf(needle)
    if (!queryWords.length) return title
    return title.split(/([^a-zA-Z0-9&]+)/).map((part, i) => {
      if (!part || /[^a-zA-Z0-9&]+/.test(part)) return part
      const qw = queryWords.find((q) => part.toLowerCase().startsWith(q))
      if (!qw) return <span key={i}>{part}</span>
      return (
        <span key={i}>
          <span className="rounded-sm bg-amber-300/90 px-0.5 font-semibold text-slate-900">
            {part.slice(0, qw.length)}
          </span>
          {part.slice(qw.length)}
        </span>
      )
    })
  }

  const filterByQuery = (items: NavItem[], needle: string): NavItem[] => {
    if (!wordsOf(needle).length) return items
    const out: NavItem[] = []
    for (const item of items) {
      const selfMatch = itemMatches(item, needle)
      const children = item.children ? filterByQuery(item.children, needle) : undefined
      if (selfMatch) {
        out.push({
          ...item,
          children: children && children.length > 0 ? children : item.children,
        })
      } else if (children && children.length > 0) {
        out.push({ ...item, children })
      }
    }
    return out
  }

  const folderIds = (items: NavItem[], parentId = ''): string[] => {
    const ids: string[] = []
    for (const item of items) {
      const id = itemId(item, parentId)
      if (item.children && item.children.length > 0) {
        ids.push(id, ...folderIds(item.children, id))
      }
    }
    return ids
  }

  const ancestorIds = (items: NavItem[], path: string, parentId = ''): string[] => {
    const found: string[] = []
    const walk = (nodes: NavItem[], parent: string): boolean => {
      for (const item of nodes) {
        const id = itemId(item, parent)
        if (item.path === path) return true
        if (item.children && item.children.length > 0 && walk(item.children, id)) {
          found.push(id)
          return true
        }
      }
      return false
    }
    walk(items, parentId)
    return found
  }

  const menuItems = useMemo(() => {
    const raw = withIcons(getGyoroomMenu(tenantName))
    return filterByModule(raw)
  }, [tenantName, isSuperuser, enabledModules.join('|'), userRole, dashHome])

  const visibleItems = useMemo(() => filterByQuery(menuItems, query), [menuItems, query])

  useEffect(() => {
    const ids = ancestorIds(menuItems, pathname)
    if (!ids.length) return
    setExpandedMenus((prev) => {
      const next = new Set(prev)
      let changed = false
      for (const id of ids) {
        if (!next.has(id)) {
          next.add(id)
          changed = true
        }
      }
      return changed ? Array.from(next) : prev
    })
  }, [pathname, menuItems])

  const toggleMenu = (id: string) => {
    setExpandedMenus((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  const searching = wordsOf(query).length > 0
  const openIds = searching ? folderIds(visibleItems) : expandedMenus

  const leafPaths = useMemo(() => {
    const paths: string[] = []
    const walk = (items: NavItem[]) => {
      for (const item of items) {
        if (item.path) paths.push(item.path)
        if (item.children) walk(item.children)
      }
    }
    walk(menuItems)
    return paths
  }, [menuItems])

  const activeLeafPath = useMemo(() => {
    return (
      leafPaths
        .filter((path) => pathname === path || pathname.startsWith(`${path}/`))
        .sort((a, b) => b.length - a.length)[0] || null
    )
  }, [leafPaths, pathname])

  useEffect(() => {
    if (!sidebarOpen || !activeLeafPath) return
    const timer = window.setTimeout(() => {
      const container = menuScrollRef.current
      const active = container?.querySelector<HTMLElement>('[data-menu-active="true"]')
      if (!container || !active) return
      // Keep the active item in the visible scroll area (with padding).
      const containerRect = container.getBoundingClientRect()
      const activeRect = active.getBoundingClientRect()
      const padding = 48
      if (activeRect.top < containerRect.top + padding) {
        container.scrollTop += activeRect.top - containerRect.top - padding
      } else if (activeRect.bottom > containerRect.bottom - padding) {
        container.scrollTop += activeRect.bottom - containerRect.bottom + padding
      }
    }, 80)
    return () => window.clearTimeout(timer)
  }, [sidebarOpen, activeLeafPath, openIds, query])

  const containsActivePath = (item: NavItem): boolean => {
    if (item.path && activeLeafPath && (item.path === activeLeafPath || activeLeafPath.startsWith(`${item.path}/`))) {
      return true
    }
    return !!item.children?.some((child) => containsActivePath(child))
  }

  const rowClass = (active: boolean, inSection: boolean, nested: boolean) =>
    [
      'group relative flex w-full items-center gap-3 border-l-[3px] px-3 py-[9px] text-left text-[13px] leading-snug transition-colors',
      nested ? 'pl-5' : '',
      active
        ? 'border-[var(--accent)] bg-[var(--row-active)] font-semibold text-white shadow-sm'
        : inSection
          ? 'border-[var(--accent)] bg-[var(--row-active-soft)] text-white'
          : 'border-transparent text-slate-100 hover:bg-[var(--row-hover)]',
    ].join(' ')

  const rowStyle = {
    '--row-hover': ROW_HOVER,
    '--row-active': ROW_ACTIVE,
    '--row-active-soft': ROW_ACTIVE_SOFT,
    '--accent': ACCENT,
  } as CSSProperties

  const renderLeafOrFolder = (item: NavItem, level: number, parentId: string) => {
    const hasChildren = !!(item.children && item.children.length > 0)
    const id = itemId(item, parentId)
    const isExpanded = openIds.includes(id)
    const isActive = !hasChildren && !!item.path && item.path === activeLeafPath
    const inSection = hasChildren && containsActivePath(item)
    const nested = level > 0

    const label = (
      <>
        <span className={activeOrSectionIcon(isActive, inSection)}>
          {item.icon || iconForTitle(item.title)}
        </span>
        <span className={`min-w-0 flex-1 truncate ${isActive ? 'font-semibold' : 'font-normal'}`}>
          {highlightTitle(item.title, query)}
        </span>
      </>
    )

    return (
      <div key={id}>
        {hasChildren ? (
          <button
            type="button"
            className={rowClass(false, inSection, nested)}
            onClick={() => toggleMenu(id)}
            style={rowStyle}
          >
            {label}
            <ChevronRight
              className={`h-3.5 w-3.5 shrink-0 transition-transform ${
                inSection ? 'text-orange-200' : 'text-slate-400'
              } ${isExpanded ? 'rotate-90' : ''}`}
            />
          </button>
        ) : item.path ? (
          <Link
            href={item.path}
            data-menu-active={isActive ? 'true' : undefined}
            className={rowClass(isActive, false, nested)}
            style={rowStyle}
          >
            {label}
          </Link>
        ) : (
          <div className={rowClass(false, false, nested)} style={rowStyle}>
            {label}
          </div>
        )}
        {hasChildren && isExpanded && (
          <div className="border-l border-white/10 ml-4">
            {item.children?.map((child) => renderLeafOrFolder(child, level + 1, id))}
          </div>
        )}
      </div>
    )
  }

  /** Top-level module folders render as always-open section headers (Turag style). */
  const renderTopItem = (item: NavItem) => {
    const hasChildren = !!(item.children && item.children.length > 0)
    if (!hasChildren) {
      return renderLeafOrFolder(item, 0, '')
    }

    const id = itemId(item, '')
    return (
      <div key={id} className="mb-0.5">
        <div
          className="px-3 py-2 text-[11px] font-semibold tracking-[0.08em] text-slate-300 uppercase"
          style={{ backgroundColor: SECTION_BG }}
        >
          {item.title}
        </div>
        <div>
          {item.children?.map((child) => renderLeafOrFolder(child, 0, id))}
        </div>
      </div>
    )
  }

  if (!sidebarOpen) {
    return (
      <button
        type="button"
        onClick={() => setSidebarOpen(true)}
        title="Show menubar"
        aria-label="Show menubar"
        className="fixed left-3 top-3 z-50 inline-flex h-10 w-10 items-center justify-center rounded border border-slate-500 text-white shadow-lg"
        style={{ backgroundColor: SIDEBAR_BG }}
      >
        <PanelLeftOpen className="h-5 w-5" />
      </button>
    )
  }

  return (
    <div
      className="fixed left-0 top-0 z-50 flex h-screen w-64 flex-col overflow-hidden text-slate-100"
      style={{ backgroundColor: SIDEBAR_BG }}
    >
      {/* Logo + hide toggle */}
      <div className="flex items-center gap-2 border-b border-white/10 px-3 py-3">
        <Link href={dashHome || '/home'} className="min-w-0 flex-1">
          {isTurag || tenantLogo ? (
            <span className="inline-flex w-full items-center justify-center rounded-sm bg-white px-2 py-1.5">
              <img
                src={tenantLogo || TURAG_CONTENT.images.logo}
                alt={tenantName}
                className="h-10 w-auto max-w-full object-contain"
              />
            </span>
          ) : (
            <span className="inline-flex items-center gap-2 text-white">
              <span className="flex h-8 w-8 items-center justify-center rounded-sm bg-white">
                <Home className="h-4 w-4 text-slate-700" />
              </span>
              <span className="truncate text-sm font-semibold">Hotel ERP</span>
            </span>
          )}
        </Link>
        <Link
          href="/apps"
          title="Apps Center"
          aria-label="Apps Center"
          className={`shrink-0 inline-flex h-9 w-9 items-center justify-center rounded-md border transition ${
            pathname === '/apps' || pathname.startsWith('/apps/')
              ? 'border-orange-400 bg-orange-500 text-white'
              : 'border-white/20 bg-white/10 text-white hover:bg-white/20'
          }`}
        >
          <LayoutGrid className="h-5 w-5" strokeWidth={1.75} />
        </Link>
        <button
          type="button"
          role="switch"
          aria-checked={sidebarOpen}
          aria-label="Hide menubar"
          title="Hide menubar"
          onClick={() => setSidebarOpen(false)}
          className="shrink-0 text-white/90 hover:text-white"
        >
          <ToggleRight className="h-6 w-6" strokeWidth={1.5} />
        </button>
      </div>

      {/* Apps Center launcher */}
      <div className="border-b border-white/10 px-3 py-2">
        <Link
          href="/apps"
          className={`flex w-full items-center gap-2.5 rounded-md px-3 py-2.5 text-[13px] font-semibold transition ${
            pathname === '/apps' || pathname.startsWith('/apps/')
              ? 'bg-[#e85d3b] text-white shadow-sm'
              : 'bg-white/10 text-white hover:bg-white/15'
          }`}
        >
          <LayoutGrid className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} />
          <span>Apps Center</span>
        </Link>
      </div>

      {/* Compact search */}
      <div className="border-b border-white/10 px-3 py-2">
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search menu..."
            autoComplete="off"
            spellCheck={false}
            className="w-full rounded-sm border border-white/10 bg-white/5 py-1.5 pl-8 pr-2 text-xs text-slate-100 placeholder:text-slate-400 focus:border-white/25 focus:outline-none"
          />
        </div>
      </div>

      {/* Menu */}
      <div
        ref={menuScrollRef}
        className="sidebar-scroll min-h-0 flex-1 overflow-y-auto"
        style={{ scrollbarColor: `${ACCENT} transparent` }}
      >
        {visibleItems.map((item) => renderTopItem(item))}
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 px-2 py-2">
        <div className="mb-1 truncate px-2 text-[11px] text-slate-400">
          {user?.first_name} {user?.last_name}
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-sm px-3 py-2 text-[13px] text-slate-100 hover:bg-[var(--row-hover)]"
          style={{ ['--row-hover' as string]: ROW_HOVER }}
        >
          <LogOut className="h-4 w-4 opacity-80" strokeWidth={1.5} />
          Logout
        </button>
      </div>
    </div>
  )
}
