'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import apiClient from '@/lib/api'
import { useRouter } from 'next/navigation'
import { ChefHat, Plus, Trash2, Loader2 } from 'lucide-react'

type IngredientOpt = { id: number; name: string; unit: string; current_stock: number }
type MenuOpt = { id: number; name: string }
type Line = { ingredient_id: string; quantity: string; unit: string }

export default function RecipeEditor({ recipeId }: { recipeId?: number }) {
  const router = useRouter()
  const [loading, setLoading] = useState(!!recipeId)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [ingredients, setIngredients] = useState<IngredientOpt[]>([])
  const [menuItems, setMenuItems] = useState<MenuOpt[]>([])
  const [form, setForm] = useState({
    name: '',
    category: 'Mains',
    servings: 1,
    preparation_time: 15,
    cooking_time: 0,
    instructions: '',
    description: '',
    menu_item_id: '',
  })
  const [lines, setLines] = useState<Line[]>([{ ingredient_id: '', quantity: '', unit: 'kg' }])

  useEffect(() => {
    const boot = async () => {
      try {
        const [ingRes, menuRes] = await Promise.all([
          apiClient.get('/fnb/ingredients'),
          apiClient.get('/fnb/menus'),
        ])
        setIngredients(ingRes.data.ingredients || [])
        const items: MenuOpt[] = []
        for (const menu of menuRes.data.menus || []) {
          for (const item of menu.items || []) {
            items.push({ id: item.id, name: `${item.name} (${menu.name})` })
          }
        }
        setMenuItems(items)
        if (recipeId) {
          const res = await apiClient.get(`/fnb/recipes/${recipeId}`)
          const r = res.data.recipe
          setForm({
            name: r.name || '',
            category: r.category || 'Mains',
            servings: r.servings || 1,
            preparation_time: r.preparation_time || 0,
            cooking_time: r.cooking_time || 0,
            instructions: r.instructions || '',
            description: r.description || '',
            menu_item_id: r.menu_item_id ? String(r.menu_item_id) : '',
          })
          setLines(
            (r.ingredients || []).map((line: any) => ({
              ingredient_id: String(line.ingredient_id),
              quantity: String(line.quantity),
              unit: line.unit || 'kg',
            }))
          )
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Could not load recipe tools')
      } finally {
        setLoading(false)
      }
    }
    boot()
  }, [recipeId])

  const addLine = () => setLines((prev) => [...prev, { ingredient_id: '', quantity: '', unit: 'kg' }])
  const removeLine = (idx: number) => setLines((prev) => prev.filter((_, i) => i !== idx))

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    const payload = {
      ...form,
      servings: Number(form.servings) || 1,
      menu_item_id: form.menu_item_id ? Number(form.menu_item_id) : null,
      ingredients: lines
        .filter((l) => l.ingredient_id && Number(l.quantity) > 0)
        .map((l) => ({
          ingredient_id: Number(l.ingredient_id),
          quantity: Number(l.quantity),
          unit: l.unit,
        })),
    }
    try {
      if (recipeId) {
        await apiClient.patch(`/fnb/recipes/${recipeId}`, payload)
      } else {
        await apiClient.post('/fnb/recipes', payload)
      }
      router.push('/fnb/recipes')
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
        <main className="flex-1 overflow-y-auto ml-64">
          <div className="p-6 max-w-4xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <ChefHat className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{recipeId ? 'Edit recipe' : 'New recipe'}</h1>
                <p className="text-gray-600 mt-1">Bill of materials used to deduct kitchen stock when this dish is ordered</p>
              </div>
            </div>
            {error && <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
            {loading ? (
              <div className="flex h-40 items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
              </div>
            ) : (
              <form onSubmit={save} className="space-y-5 rounded-xl border bg-white p-6 shadow-sm">
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="text-sm sm:col-span-2">
                    <span className="mb-1 block text-gray-600">Recipe name</span>
                    <input required className="w-full rounded-lg border px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                  </label>
                  <label className="text-sm">
                    <span className="mb-1 block text-gray-600">Category</span>
                    <input className="w-full rounded-lg border px-3 py-2" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
                  </label>
                  <label className="text-sm">
                    <span className="mb-1 block text-gray-600">Servings (per recipe)</span>
                    <input type="number" min={1} className="w-full rounded-lg border px-3 py-2" value={form.servings} onChange={(e) => setForm({ ...form, servings: Number(e.target.value) })} />
                  </label>
                  <label className="text-sm">
                    <span className="mb-1 block text-gray-600">Prep time (min)</span>
                    <input type="number" min={0} className="w-full rounded-lg border px-3 py-2" value={form.preparation_time} onChange={(e) => setForm({ ...form, preparation_time: Number(e.target.value) })} />
                  </label>
                  <label className="text-sm">
                    <span className="mb-1 block text-gray-600">Link to menu item</span>
                    <select className="w-full rounded-lg border px-3 py-2" value={form.menu_item_id} onChange={(e) => setForm({ ...form, menu_item_id: e.target.value })}>
                      <option value="">Not linked</option>
                      {menuItems.map((m) => (
                        <option key={m.id} value={m.id}>{m.name}</option>
                      ))}
                    </select>
                  </label>
                </div>
                <label className="block text-sm">
                  <span className="mb-1 block text-gray-600">Instructions</span>
                  <textarea rows={3} className="w-full rounded-lg border px-3 py-2" value={form.instructions} onChange={(e) => setForm({ ...form, instructions: e.target.value })} />
                </label>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <h2 className="font-medium">Ingredients per serving</h2>
                    <button type="button" onClick={addLine} className="inline-flex items-center gap-1 text-sm text-indigo-600">
                      <Plus className="h-4 w-4" /> Add line
                    </button>
                  </div>
                  <div className="space-y-2">
                    {lines.map((line, idx) => (
                      <div key={idx} className="grid grid-cols-[1fr_120px_90px_40px] gap-2">
                        <select
                          className="rounded-lg border px-2 py-2 text-sm"
                          value={line.ingredient_id}
                          onChange={(e) => {
                            const ing = ingredients.find((i) => String(i.id) === e.target.value)
                            setLines((prev) => prev.map((l, i) => i === idx ? { ...l, ingredient_id: e.target.value, unit: ing?.unit || l.unit } : l))
                          }}
                        >
                          <option value="">Select ingredient</option>
                          {ingredients.map((ing) => (
                            <option key={ing.id} value={ing.id}>{ing.name} ({ing.current_stock} {ing.unit} in stock)</option>
                          ))}
                        </select>
                        <input
                          type="number"
                          step="0.001"
                          min="0"
                          placeholder="Qty"
                          className="rounded-lg border px-2 py-2 text-sm"
                          value={line.quantity}
                          onChange={(e) => setLines((prev) => prev.map((l, i) => i === idx ? { ...l, quantity: e.target.value } : l))}
                        />
                        <input
                          className="rounded-lg border px-2 py-2 text-sm"
                          value={line.unit}
                          onChange={(e) => setLines((prev) => prev.map((l, i) => i === idx ? { ...l, unit: e.target.value } : l))}
                        />
                        <button type="button" onClick={() => removeLine(idx)} className="text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button type="submit" disabled={saving} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">
                    {saving ? 'Saving…' : 'Save recipe'}
                  </button>
                  <button type="button" onClick={() => router.push('/fnb/recipes')} className="rounded-lg border px-4 py-2 text-sm">
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
