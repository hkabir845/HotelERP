'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'
import { useRouter } from 'next/navigation'
import {
  FileText,
  Search,
  Plus,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  DollarSign,
  Folder,
  File
} from 'lucide-react'

interface Account {
  id: number
  code: string
  name: string
  account_type: string
  parent_id: number | null
  balance: number
  is_group: boolean
  level: number
  children?: Account[]
}

export default function ChartOfAccountsPage() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set())

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/accounts/chart-of-accounts?${params.toString()}`)
      setAccounts(response.data.accounts || [])
    } catch (error) {
      console.error('Error fetching accounts:', error)
      setAccounts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => fetchAccounts(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const toggleGroup = (accountId: number) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev)
      if (newSet.has(accountId)) {
        newSet.delete(accountId)
      } else {
        newSet.add(accountId)
      }
      return newSet
    })
  }

  const renderAccount = (account: Account, level: number = 0) => {
    const isExpanded = expandedGroups.has(account.id)
    const hasChildren = account.children && account.children.length > 0

    return (
      <div key={account.id}>
        <div
          className={`flex items-center gap-2 px-4 py-3 hover:bg-gray-200 border-b border-gray-100 ${
            account.is_group ? 'bg-gray-200' : ''
          }`}
          style={{ paddingLeft: `${level * 24 + 16}px` }}
        >
          {account.is_group ? (
            <button
              onClick={() => toggleGroup(account.id)}
              className="p-1 hover:bg-gray-200 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-gray-600" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-600" />
              )}
            </button>
          ) : (
            <div className="w-6" />
          )}
          <div className="flex-1 grid grid-cols-4 gap-4 items-center">
            <div className="flex items-center gap-2">
              {account.is_group ? (
                <Folder className="h-4 w-4 text-blue-500" />
              ) : (
                <File className="h-4 w-4 text-gray-400" />
              )}
              <span className="text-sm font-medium text-gray-900">{account.code}</span>
            </div>
            <div className="text-sm text-gray-900">{account.name}</div>
            <div className="text-sm text-gray-600 capitalize">{account.account_type}</div>
            <div className={`text-sm font-medium text-right ${
              account.balance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatMoney(Math.abs(account.balance))}
            </div>
          </div>
        </div>
        {account.is_group && isExpanded && hasChildren && (
          <div>
            {account.children!.map(child => renderAccount(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <FileText className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Chart of Accounts</h1>
                    <p className="text-gray-600 mt-1">
                      Built-in hotel template (cash, bank, AR/AP, room/F&B/banquet, rent, loans…) — editable anytime
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/accounts/chart-of-accounts/accounts')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Account
                  </button>
                  <button
                    onClick={fetchAccounts}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by account code, name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : accounts.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No accounts found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new account</p>
                <button
                  onClick={() => router.push('/accounts/chart-of-accounts/accounts')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Account
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <div className="min-w-full">
                    <div className="bg-gray-200 border-b border-gray-200 px-4 py-3">
                      <div className="grid grid-cols-4 gap-4">
                        <div className="text-xs font-medium text-gray-500 uppercase">Code</div>
                        <div className="text-xs font-medium text-gray-500 uppercase">Account Name</div>
                        <div className="text-xs font-medium text-gray-500 uppercase">Type</div>
                        <div className="text-xs font-medium text-gray-500 uppercase text-right">Balance</div>
                      </div>
                    </div>
                    <div>
                      {accounts.map(account => renderAccount(account))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

