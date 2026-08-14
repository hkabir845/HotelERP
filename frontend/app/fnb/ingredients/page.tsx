'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { Package, Search, Plus, RefreshCw, Edit, Scale, AlertCircle, ArrowDownToLine } from 'lucide-react'
import { formatMoney } from '@/lib/money'

interface Ingredient {
  id: number
  code: string
  name: string
  category: string
  unit: string
  current_stock: number
  min_stock: number
  unit_cost: number
  supplier: string | null
  is_low_stock: boolean
}

const emptyForm = {
  name: '',
  category: 'General',
  unit: 'kg',
  unit_cost: '0',
  current_stock: '0',
  min_stock: '0',
  supplier: '',
}

export default function IngredientsPage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [error, setError] = useState('')
  const [editor, setEditor] = useState<null | { id?: number }>(null)
  const [form, setForm] = useState(emptyForm)
  const [stockFor, setStockFor] = useState<Ingredient | null>(null)
  const [stockQty, setStockQty] = useState('')
  const [stockType, setStockType] = useState('receive')
  const [stockNotes, setStockNotes] = useState('')

  const fetchIngredients = async () => {
    try {
      setLoading(true)
      setError('')
      const params = new URLSearchParams()
      if (categoryFilter !== 'all') params.append('category', categoryFilter)
      if (searchTerm) params.append('search', searchTerm)
      const response = await apiClient.get(`/fnb/ingredients?${params.toString()}`)
      setIngredients(response.data.ingredients || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not load ingredients')
      setIngredients([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIngredients()
  }, [categoryFilter])

  useEffect(() => {
    const timer = setTimeout(() => fetchIngredients(), 300)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const categories = Array.from(new Set(ingredients.map((i) => i.category).filter(Boolean)))
  const lowStockItems = ingredients.filter((i) => i.is_low_stock || i.current_stock <= i.min_stock)
  const totalValue = ingredients.reduce((sum, i) => sum + i.current_stock * i.unit_cost, 0)

  const openNew = () => {
    setForm(emptyForm)
    setEditor({})
  }
  const openEdit = (ing: Ingredient) => {
    setForm({
      name: ing.name,
      category: ing.category || 'General',
      unit: ing.unit,
      unit_cost: String(ing.unit_cost),
      current_stock: String(ing.current_stock),
      min_stock: String(ing.min_stock),
      supplier: ing.supplier || '',
    })
    setEditor({ id: ing.id })
  }

  const saveIngredient = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = {
      name: form.name,
      category: form.category,
      unit: form.unit,
      unit_cost: Number(form.unit_cost),
      min_stock: Number(form.min_stock),
      supplier: form.supplier,
      current_stock: Number(form.current_stock),
    }
    try {
      if (editor?.id) {
        await apiClient.patch(`/fnb/ingredients/${editor.id}`, payload)
      } else {
        await apiClient.post('/fnb/ingredients', payload)
      }
      setEditor(null)
      fetchIngredients()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Save failed')
    }
  }

  const saveStock = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!stockFor) return
    try {
      await apiClient.post(`/fnb/ingredients/${stockFor.id}/stock`, {
        quantity: Number(stockQty),
        movement_type: stockType,
        notes: stockNotes,
      })
      setStockFor(null)
      setStockQty('')
      setStockNotes('')
      fetchIngredients()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Stock update failed')
    }
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
                    <Package className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">Kitchen stock</h1>
                    <p className="text-gray-600 mt-1">Ingredients used in recipes. Stock deducts automatically when food is ordered.</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={openNew} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2">
                    <Plus className="h-4 w-4" /> New Ingredient
                  </button>
                  <button onClick={fetchIngredients} className="p-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-200">
                    <RefreshCw className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {error && <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Ingredients</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{ingredients.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Stock value</div>
                  <div className="text-2xl font-bold text-indigo-600 mt-1">{formatMoney(totalValue)}</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Low Stock</div>
                  <div className="text-2xl font-bold text-red-600 mt-1">{lowStockItems.length}</div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Categories</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">{categories.length}</div>
                </div>
              </div>

              {lowStockItems.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="font-medium text-red-900">
                      {lowStockItems.map((i) => i.name).join(', ')} {lowStockItems.length === 1 ? 'is' : 'are'} at or below minimum stock
                    </span>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex-1 min-w-[200px] relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search ingredients..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg">
                    <option value="all">All Categories</option>
                    {categories.map((cat) => (
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
            ) : ingredients.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No ingredients found</h3>
                <button onClick={openNew} className="px-4 py-2 bg-indigo-600 text-white rounded-lg">Add Ingredient</button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Cost</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {ingredients.map((ingredient) => {
                      const isLowStock = ingredient.is_low_stock || ingredient.current_stock <= ingredient.min_stock
                      return (
                        <tr key={ingredient.id} className={isLowStock ? 'bg-red-50' : 'hover:bg-gray-100'}>
                          <td className="px-6 py-4 text-sm font-medium">{ingredient.code}</td>
                          <td className="px-6 py-4 text-sm">
                            {ingredient.name}
                            <div className="text-xs text-gray-500">{ingredient.category}</div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`text-sm font-medium ${isLowStock ? 'text-red-600' : ''}`}>
                              {ingredient.current_stock}
                            </span>
                            {isLowStock && <AlertCircle className="inline h-4 w-4 text-red-600 ml-1" />}
                            <div className="text-xs text-gray-500">min {ingredient.min_stock}</div>
                          </td>
                          <td className="px-6 py-4 text-sm">
                            <Scale className="inline h-3 w-3 text-gray-400 mr-1" />
                            {ingredient.unit}
                          </td>
                          <td className="px-6 py-4 text-sm">{formatMoney(ingredient.unit_cost)}</td>
                          <td className="px-6 py-4 text-sm text-indigo-600">{formatMoney(ingredient.current_stock * ingredient.unit_cost)}</td>
                          <td className="px-6 py-4 text-right">
                            <button onClick={() => setStockFor(ingredient)} className="mr-3 text-emerald-700" title="Receive / adjust stock">
                              <ArrowDownToLine className="h-4 w-4" />
                            </button>
                            <button onClick={() => openEdit(ingredient)} className="text-indigo-600">
                              <Edit className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>

      {editor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form onSubmit={saveIngredient} className="w-full max-w-lg space-y-3 rounded-xl bg-white p-6">
            <h2 className="text-lg font-semibold">{editor.id ? 'Edit ingredient' : 'New ingredient'}</h2>
            <input required className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <div className="grid grid-cols-2 gap-3">
              <input className="rounded-lg border px-3 py-2 text-sm" placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
              <input className="rounded-lg border px-3 py-2 text-sm" placeholder="Unit (kg, l, pcs)" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
              <input type="number" step="0.01" className="rounded-lg border px-3 py-2 text-sm" placeholder="Unit cost" value={form.unit_cost} onChange={(e) => setForm({ ...form, unit_cost: e.target.value })} />
              <input type="number" step="0.01" className="rounded-lg border px-3 py-2 text-sm" placeholder="Min stock" value={form.min_stock} onChange={(e) => setForm({ ...form, min_stock: e.target.value })} />
              {!editor.id && (
                <input type="number" step="0.01" className="rounded-lg border px-3 py-2 text-sm col-span-2" placeholder="Opening stock" value={form.current_stock} onChange={(e) => setForm({ ...form, current_stock: e.target.value })} />
              )}
              <input className="rounded-lg border px-3 py-2 text-sm col-span-2" placeholder="Supplier" value={form.supplier} onChange={(e) => setForm({ ...form, supplier: e.target.value })} />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEditor(null)} className="rounded-lg border px-4 py-2 text-sm">Cancel</button>
              <button type="submit" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">Save</button>
            </div>
          </form>
        </div>
      )}

      {stockFor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form onSubmit={saveStock} className="w-full max-w-md space-y-3 rounded-xl bg-white p-6">
            <h2 className="text-lg font-semibold">Stock · {stockFor.name}</h2>
            <p className="text-sm text-gray-600">On hand: {stockFor.current_stock} {stockFor.unit}</p>
            <select className="w-full rounded-lg border px-3 py-2 text-sm" value={stockType} onChange={(e) => setStockType(e.target.value)}>
              <option value="receive">Receive (purchase / delivery)</option>
              <option value="adjust">Adjustment</option>
              <option value="waste">Waste / spoilage</option>
            </select>
            <input required type="number" step="0.001" className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Quantity" value={stockQty} onChange={(e) => setStockQty(e.target.value)} />
            <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Notes" value={stockNotes} onChange={(e) => setStockNotes(e.target.value)} />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setStockFor(null)} className="rounded-lg border px-4 py-2 text-sm">Cancel</button>
              <button type="submit" className="rounded-lg bg-emerald-700 px-4 py-2 text-sm text-white">Update stock</button>
            </div>
          </form>
        </div>
      )}
    </ProtectedRoute>
  )
}
