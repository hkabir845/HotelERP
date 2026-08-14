'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import {
  Settings,
  Save,
  Loader2,
  CheckCircle2,
  Globe,
  DollarSign,
  Mail,
  Bell,
  Shield
} from 'lucide-react'

interface SystemSettings {
  hotel_name: string
  currency: string
  timezone: string
  date_format: string
  email_enabled: boolean
  sms_enabled: boolean
  notification_enabled: boolean
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings>({
    hotel_name: '',
    currency: 'BDT',
    timezone: 'Asia/Dhaka',
    date_format: 'YYYY-MM-DD',
    email_enabled: true,
    sms_enabled: false,
    notification_enabled: true
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/utilities/settings')
      setSettings(response.data.settings || settings)
    } catch (error) {
      console.error('Error fetching settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setSuccess(false)

    try {
      await apiClient.put('/utilities/settings', settings)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (error: any) {
      console.error('Error saving settings:', error)
      alert(error.response?.data?.detail || 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Settings className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
                  <p className="text-gray-600 mt-1">Configure system preferences and options</p>
                </div>
              </div>
            </div>

            {success && (
              <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <p className="font-medium text-green-900">Settings saved successfully!</p>
              </div>
            )}

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="max-w-4xl">
                <div className="space-y-6">
                  {/* General Settings */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Globe className="h-5 w-5 text-indigo-600" />
                      General Settings
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Hotel Name
                        </label>
                        <input
                          type="text"
                          value={settings.hotel_name}
                          onChange={(e) => setSettings({ ...settings, hotel_name: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Currency
                        </label>
                        <select
                          value={settings.currency}
                          onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="BDT">BDT - Bangladeshi Taka</option>
                          <option value="USD">USD - US Dollar</option>
                          <option value="EUR">EUR - Euro</option>
                          <option value="GBP">GBP - British Pound</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Timezone
                        </label>
                        <select
                          value={settings.timezone}
                          onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="Asia/Dhaka">Asia/Dhaka</option>
                          <option value="UTC">UTC</option>
                          <option value="America/New_York">America/New_York</option>
                          <option value="Europe/London">Europe/London</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Date Format
                        </label>
                        <select
                          value={settings.date_format}
                          onChange={(e) => setSettings({ ...settings, date_format: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                          <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                          <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Notification Settings */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Bell className="h-5 w-5 text-indigo-600" />
                      Notification Settings
                    </h2>
                    <div className="space-y-4">
                      <label className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={settings.email_enabled}
                          onChange={(e) => setSettings({ ...settings, email_enabled: e.target.checked })}
                          className="rounded"
                        />
                        <div>
                          <span className="font-medium text-gray-900">Email Notifications</span>
                          <p className="text-sm text-gray-600">Enable email notifications for system events</p>
                        </div>
                      </label>
                      <label className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={settings.sms_enabled}
                          onChange={(e) => setSettings({ ...settings, sms_enabled: e.target.checked })}
                          className="rounded"
                        />
                        <div>
                          <span className="font-medium text-gray-900">SMS Notifications</span>
                          <p className="text-sm text-gray-600">Enable SMS notifications</p>
                        </div>
                      </label>
                      <label className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={settings.notification_enabled}
                          onChange={(e) => setSettings({ ...settings, notification_enabled: e.target.checked })}
                          className="rounded"
                        />
                        <div>
                          <span className="font-medium text-gray-900">In-App Notifications</span>
                          <p className="text-sm text-gray-600">Enable in-app notification system</p>
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-end gap-4">
                    <button
                      type="submit"
                      disabled={saving}
                      className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {saving ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4" />
                          Save Settings
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

