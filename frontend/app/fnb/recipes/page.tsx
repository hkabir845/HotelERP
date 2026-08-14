'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import {
  ChefHat,
  Search,
  Plus,
  RefreshCw,
  Eye,
  Edit,
  DollarSign,
  Package,
  Clock
} from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Recipe {
  id: number
  recipe_code: string
  name: string
  category: string
  serving_size: number
  preparation_time: number
  cost_per_serving: number
  selling_price: number
  profit_margin: number
  ingredients_count: number
  status: string
}

export default function RecipesPage() {
  const router = useRouter()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [error, setError] = useState('')

  const fetchRecipes = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (categoryFilter !== 'all') params.append('category', categoryFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await apiClient.get(`/fnb/recipes?${params.toString()}`)
      setRecipes(response.data.recipes || [])
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not load recipes')
      setRecipes([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecipes()
  }, [categoryFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchRecipes(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const categories = Array.from(new Set(recipes.map(r => r.category)))
  const totalCost = recipes.reduce((sum, r) => sum + r.cost_per_serving, 0)
  const totalRevenue = recipes.reduce((sum, r) => sum + r.selling_price, 0)
  const totalProfit = totalRevenue - totalCost

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
                    <ChefHat className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Recipes</h1>
                    <p className="text-gray-600 mt-1">Company recipes. Each dish deducts ingredient stock when ordered.</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => router.push('/fnb/recipes/new')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    New Recipe
                  </button>
                  <button
                    onClick={fetchRecipes}
                    className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {error && (
                <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
              )}

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Recipes</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{recipes.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Cost</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{formatMoney(totalCost)}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Revenue</div>
                  <div className="text-2xl font-bold text-indigo-600 mt-1">{formatMoney(totalRevenue)}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Profit</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">{formatMoney(totalProfit)}</div>
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
                        placeholder="Search by recipe name, code..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="all">All Categories</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : recipes.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <ChefHat className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No recipes found</h3>
                <p className="text-gray-600 mb-4">Get started by creating a new recipe</p>
                <button
                  onClick={() => router.push('/fnb/recipes/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Recipe
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recipe Code</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Serving Size</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prep Time</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit Margin</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ingredients</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {recipes.map((recipe) => (
                        <tr key={recipe.id} className="hover:bg-gray-200">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {recipe.recipe_code}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {recipe.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {recipe.category}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {recipe.serving_size}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3 text-gray-400" />
                              {recipe.preparation_time} min
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">
                            {formatMoney(recipe.cost_per_serving)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                            {formatMoney(recipe.selling_price)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`text-sm font-medium ${
                              recipe.profit_margin > 50 ? 'text-green-600' :
                              recipe.profit_margin > 30 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {recipe.profit_margin.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div className="flex items-center gap-1">
                              <Package className="h-3 w-3 text-gray-400" />
                              {recipe.ingredients_count}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => router.push(`/fnb/recipes/${recipe.id}`)}
                                className="text-indigo-600 hover:text-indigo-900"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => router.push(`/fnb/recipes/${recipe.id}/edit`)}
                                className="text-gray-600 hover:text-gray-900"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

