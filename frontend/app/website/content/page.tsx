'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import LandingContentEditor from '@/components/saas/LandingContentEditor'
import apiClient from '@/lib/api'
import { DEFAULT_TURAG_CONTENT, mergeLandingContent } from '@/lib/landings/turag-content'

export default function WebsiteContentPage() {
  const [content, setContent] = useState<any>(DEFAULT_TURAG_CONTENT)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get('/website/content')
      .then((res) => setContent(mergeLandingContent(res.data.landing_content)))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load website content'))
  }, [])

  const save = async () => {
    setSaving(true)
    setMessage('')
    setError('')
    try {
      const res = await apiClient.patch('/website/content', { landing_content: content })
      setContent(mergeLandingContent(res.data.landing_content))
      setMessage('Website content saved. Public site refreshes within 30 seconds.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Website content</h1>
              <p className="mt-1 text-gray-600">Hero, about, gallery, blog, activities, and venue copy.</p>
            </div>
            <button
              type="button"
              onClick={save}
              disabled={saving}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
          {message && <p className="mb-4 text-emerald-700">{message}</p>}
          {error && <p className="mb-4 text-red-600">{error}</p>}
          <div className="rounded-xl border bg-white p-6">
            <LandingContentEditor value={content} onChange={setContent} />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
