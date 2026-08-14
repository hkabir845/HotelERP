'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { ChefHat, Package } from 'lucide-react'
import { formatMoney } from '@/lib/money'

export default function RecipeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [recipe, setRecipe] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .get(`/fnb/recipes/${params.id}`)
      .then((res) => setRecipe(res.data.recipe))
      .catch((err) => setError(err.response?.data?.detail || 'Recipe not found'))
  }, [params.id])

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6 max-w-3xl">
            <button onClick={() => router.push('/fnb/recipes')} className="text-sm text-indigo-600 hover:underline">
              ← Recipes
            </button>
            {error && <div className="mt-4 rounded-lg bg-red-50 p-4 text-red-700">{error}</div>}
            {recipe && (
              <div className="mt-4 rounded-xl border bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-indigo-100 p-2">
                      <ChefHat className="h-6 w-6 text-indigo-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{recipe.recipe_code}</p>
                      <h1 className="text-2xl font-bold">{recipe.name}</h1>
                      <p className="text-sm text-gray-600">{recipe.category} · {recipe.serving_size} serving</p>
                    </div>
                  </div>
                  <button
                    onClick={() => router.push(`/fnb/recipes/${recipe.id}/edit`)}
                    className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white"
                  >
                    Edit
                  </button>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-3 text-sm">
                  <div className="rounded-lg bg-gray-50 p-3">
                    <p className="text-gray-500">Food cost</p>
                    <p className="text-lg font-semibold">{formatMoney(recipe.cost_per_serving)}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3">
                    <p className="text-gray-500">Menu price</p>
                    <p className="text-lg font-semibold">{formatMoney(recipe.selling_price)}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3">
                    <p className="text-gray-500">Margin</p>
                    <p className="text-lg font-semibold">{Number(recipe.profit_margin).toFixed(1)}%</p>
                  </div>
                </div>
                <h2 className="mt-6 mb-2 flex items-center gap-2 font-medium">
                  <Package className="h-4 w-4" /> Ingredients deducted per order
                </h2>
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500">
                      <th className="py-2">Item</th>
                      <th>Qty</th>
                      <th>In stock</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(recipe.ingredients || []).map((line: any) => (
                      <tr key={line.id} className="border-t">
                        <td className="py-2">{line.name}</td>
                        <td>{line.quantity} {line.unit}</td>
                        <td className={line.current_stock <= 0 ? 'text-red-600' : ''}>{line.current_stock} {line.unit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {recipe.instructions && <p className="mt-4 whitespace-pre-wrap text-sm text-gray-700">{recipe.instructions}</p>}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
