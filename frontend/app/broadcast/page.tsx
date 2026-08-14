'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  MessageSquare,
  Search,
  Plus,
  RefreshCw,
  Send,
  Users,
  Calendar,
  Bell,
  CheckCircle2
} from 'lucide-react'

interface Message {
  id: number
  message_number: string
  subject: string
  content: string
  recipient_type: string
  recipients: string[]
  status: string
  sent_at: string | null
  created_at?: string | null
  created_by: string
}

export default function BroadcastMessagesPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    draft: { label: 'Draft', color: 'text-gray-700', bgColor: 'bg-gray-100' },
    scheduled: { label: 'Scheduled', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    sent: { label: 'Sent', color: 'text-green-700', bgColor: 'bg-green-100' },
    failed: { label: 'Failed', color: 'text-red-700', bgColor: 'bg-red-100' }
  }

  const fetchMessages = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/broadcast/messages?${params.toString()}`)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Error fetching messages:', error)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchMessages(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
                    <MessageSquare className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Broadcast Messages</h1>
                    <p className="text-gray-600 mt-1">Send messages to guests, staff, or departments</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/broadcast/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Message
                  </button>
                  <button
                    onClick={fetchMessages}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Messages</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{messages.length}</div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Sent</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {messages.filter(m => m.status === 'sent').length}
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Scheduled</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {messages.filter(m => m.status === 'scheduled').length}
                  </div>
                </div>
                <div className="bg-gray-200 border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Drafts</div>
                  <div className="text-2xl font-bold text-gray-600 mt-1">
                    {messages.filter(m => m.status === 'draft').length}
                  </div>
                </div>
              </div>

              {/* Filters */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search by subject, message #..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="all">All Statuses</option>
                    {Object.entries(statusConfig).map(([value, config]) => (
                      <option key={value} value={value}>{config.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : messages.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No messages found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new message</p>
                <button
                  onClick={() => router.push('/broadcast/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Message
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => {
                  const status = statusConfig[message.status] || statusConfig.draft
                  return (
                    <div key={message.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{message.subject}</h3>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                              {status.label}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mb-2">{message.content.substring(0, 150)}...</div>
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              <Users className="h-4 w-4" />
                              <span className="capitalize">{message.recipient_type}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(message.sent_at || message.created_at || null)}
                            </div>
                            <div className="flex items-center gap-1">
                              <Bell className="h-4 w-4" />
                              {message.recipients.length} recipient{message.recipients.length !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        <div className="ml-4">
                          {message.status === 'sent' && (
                            <CheckCircle2 className="h-6 w-6 text-green-600" />
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

