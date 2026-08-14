'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { BookOpen, RefreshCw } from 'lucide-react'
import { formatMoney } from '@/lib/money'

export default function MenusPage() {
  const [menus, setMenus] = useState<any[]>([])
  const [recipes, setRecipes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [newName, setNewName] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [menuRes, recipeRes] = await Promise.all([
        apiClient.get('/fnb/menus'),
        apiClient.get('/fnb/recipes').catch(() => ({ data: { recipes: [] } })),
      ])
      setMenus(menuRes.data.menus || [])
      setRecipes(recipeRes.data.recipes || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not load menus')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const createMenu = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    await apiClient.post('/fnb/menus', { name: newName })
    setNewName('')
    load()
  }

  const linkRecipe = async (itemId: number, recipeId: string) => {
    await apiClient.patch(`/fnb/menu-items/${itemId}`, {
      recipe_id: recipeId ? Number(recipeId) : null,
    })
    load()
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <BookOpen className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Menu management</h1>
                  <p className="text-gray-600 mt-1">Link each dish to a recipe so kitchen stock deducts on every order</p>
                </div>
              </div>
              <button onClick={load} className="p-2 bg-white border rounded-lg">
                <RefreshCw className="h-5 w-5" />
              </button>
            </div>
            {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
            <form onSubmit={createMenu} className="mb-6 flex gap-2">
              <input className="rounded-lg border px-3 py-2 text-sm" placeholder="New menu name" value={newName} onChange={(e) => setNewName(e.target.value)} />
              <button className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">Add menu</button>
            </form>
            {loading ? (
              <div className="py-16 text-center text-gray-500">Loading menus…</div>
            ) : (
              <div className="space-y-6">
                {menus.map((menu) => (
                  <section key={menu.id} className="rounded-xl border bg-white p-5 shadow-sm">
                    <h2 className="text-lg font-semibold">{menu.name}</h2>
                    <p className="text-sm text-gray-500">{menu.items_count} items · shown on POS and the public website</p>
                    <table className="mt-3 min-w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-500">
                          <th className="py-2">Dish</th>
                          <th>Price</th>
                          <th>Recipe (stock BOM)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(menu.items || []).map((item: any) => (
                          <tr key={item.id} className="border-t">
                            <td className="py-2">
                              {item.name}
                              <div className="text-xs text-gray-500">{item.category}</div>
                            </td>
                            <td>{formatMoney(item.price)}</td>
                            <td>
                              <select
                                className="rounded-lg border px-2 py-1 text-sm"
                                value={item.recipe_id || ''}
                                onChange={(e) => linkRecipe(item.id, e.target.value)}
                              >
                                <option value="">No recipe — no stock deduct</option>
                                {recipes.map((r) => (
                                  <option key={r.id} value={r.id}>{r.name}</option>
                                ))}
                              </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </section>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
