'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { formatMoney } from '@/lib/money'

export default function HrDashboard() {
  const [cards, setCards] = useState<{ label: string; value: number }[]>([])
  const [today, setToday] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get('/hr/dashboard')
      .then((res) => {
        setCards(res.data.cards || [])
        setToday(res.data.today || '')
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load'))
  }, [])

  const moneyish = (label: string, value: number) =>
    label.toLowerCase().includes('net')
      ? formatMoney(value)
      : String(value)

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">HR Dashboard</h1>
          <p className="mt-1 text-gray-600">Staff, attendance, leave, loans, and payroll for {today || 'today'}.</p>
          {error && <p className="mt-4 text-red-600">{error}</p>}
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {cards.map((card) => (
              <div key={card.label} className="rounded-xl border bg-white p-4">
                <div className="text-sm text-slate-500">{card.label}</div>
                <div className="mt-1 text-2xl font-semibold">{moneyish(card.label, card.value)}</div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3 text-sm">
            <Link className="rounded-lg bg-indigo-600 px-4 py-2 text-white" href="/hr/attendance/punch">
              Punch in/out
            </Link>
            <Link className="rounded-lg border bg-white px-4 py-2" href="/hr/leave-requests">
              Leave requests
            </Link>
            <Link className="rounded-lg border bg-white px-4 py-2" href="/hr/payroll">
              Payroll
            </Link>
            <Link className="rounded-lg border bg-white px-4 py-2" href="/hr/loans">
              Loans
            </Link>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
