'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { TrendingUp, AlertCircle } from 'lucide-react'
import { formatMoney } from '@/lib/money'

export default function CostAnalysisPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get('/fnb/recipes/cost-analysis')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Cost analysis unavailable'))
  }, [])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Cost analysis</h1>
                <p className="text-gray-600 mt-1">Food cost from recipes vs menu selling prices, plus kitchen stock health</p>
              </div>
            </div>
            {error && <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>}
            {data && (
              <>
                <div className="mb-6 grid gap-4 sm:grid-cols-4">
                  <div className="rounded-xl border bg-white p-4">
                    <p className="text-sm text-gray-500">Recipes</p>
                    <p className="text-2xl font-bold">{data.recipe_count}</p>
                  </div>
                  <div className="rounded-xl border bg-white p-4">
                    <p className="text-sm text-gray-500">Avg food cost</p>
                    <p className="text-2xl font-bold text-red-600">{formatMoney(data.avg_food_cost)}</p>
                  </div>
                  <div className="rounded-xl border bg-white p-4">
                    <p className="text-sm text-gray-500">Menu revenue (list)</p>
                    <p className="text-2xl font-bold text-indigo-600">{formatMoney(data.menu_revenue)}</p>
                  </div>
                  <div className="rounded-xl border bg-white p-4">
                    <p className="text-sm text-gray-500">Kitchen stock value</p>
                    <p className="text-2xl font-bold">{formatMoney(data.stock_value)}</p>
                  </div>
                </div>
                {data.low_stock_count > 0 && (
                  <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
                    <AlertCircle className="mr-2 inline h-4 w-4" />
                    {data.low_stock_count} ingredients below minimum: {(data.low_stock || []).map((i: any) => i.name).join(', ')}
                  </div>
                )}
                <div className="overflow-hidden rounded-xl border bg-white">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-100 text-left text-gray-500">
                      <tr>
                        <th className="px-4 py-3">Recipe</th>
                        <th>Cost</th>
                        <th>Sell</th>
                        <th>Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(data.recipes || []).map((r: any) => (
                        <tr key={r.id} className="border-t">
                          <td className="px-4 py-3">
                            {r.name}
                            <div className="text-xs text-gray-500">{r.category}</div>
                          </td>
                          <td>{formatMoney(r.cost_per_serving)}</td>
                          <td>{formatMoney(r.selling_price)}</td>
                          <td className={Number(r.profit_margin) < 30 ? 'text-red-600' : 'text-emerald-700'}>
                            {Number(r.profit_margin).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
