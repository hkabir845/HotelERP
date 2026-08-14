'use client'

import { useParams } from 'next/navigation'
import RecipeEditor from '@/components/fnb/RecipeEditor'

export default function EditRecipePage() {
  const params = useParams()
  return <RecipeEditor recipeId={Number(params.id)} />
}
