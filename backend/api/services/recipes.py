"""Recipe management: ingredients, BOM, kitchen stock, order deduction."""
from decimal import Decimal

from django.db import transaction

from api.models import (
    Ingredient,
    IngredientStockMovement,
    Menu,
    MenuItem,
    Order,
    Recipe,
    RecipeIngredient,
    StockMovementType,
)

SEED_INGREDIENTS = [
    ('Chicken Breast', 'Meat', 'kg', Decimal('8.5000'), Decimal('20'), Decimal('8')),
    ('Beef', 'Meat', 'kg', Decimal('12.0000'), Decimal('15'), Decimal('6')),
    ('River Fish', 'Seafood', 'kg', Decimal('10.0000'), Decimal('12'), Decimal('5')),
    ('Romaine Lettuce', 'Vegetables', 'kg', Decimal('2.5000'), Decimal('8'), Decimal('3')),
    ('Garden Vegetables', 'Vegetables', 'kg', Decimal('2.2000'), Decimal('10'), Decimal('4')),
    ('Tomato', 'Vegetables', 'kg', Decimal('1.8000'), Decimal('8'), Decimal('3')),
    ('Pasta', 'Dry goods', 'kg', Decimal('1.5000'), Decimal('12'), Decimal('4')),
    ('Basmati Rice', 'Dry goods', 'kg', Decimal('1.4000'), Decimal('20'), Decimal('8')),
    ('Lime', 'Produce', 'kg', Decimal('1.2000'), Decimal('6'), Decimal('2')),
    ('Coffee Beans', 'Beverage', 'kg', Decimal('14.0000'), Decimal('5'), Decimal('2')),
    ('Dark Chocolate', 'Dry goods', 'kg', Decimal('9.0000'), Decimal('4'), Decimal('1.5')),
    ('Seasonal Fruit', 'Produce', 'kg', Decimal('3.0000'), Decimal('8'), Decimal('3')),
]

# quantity is per 1 serving
SEED_RECIPES = [
    ('Chicken Caesar Salad', 'Salad', 12, [
        ('Chicken Breast', Decimal('0.120')),
        ('Romaine Lettuce', Decimal('0.080')),
        ('Lime', Decimal('0.020')),
    ]),
    ('Seasonal Garden Salad', 'Salad', 8, [
        ('Romaine Lettuce', Decimal('0.100')),
        ('Garden Vegetables', Decimal('0.080')),
        ('Tomato', Decimal('0.040')),
    ]),
    ('Grilled River Fish', 'Mains', 20, [
        ('River Fish', Decimal('0.220')),
        ('Basmati Rice', Decimal('0.150')),
        ('Lime', Decimal('0.030')),
        ('Garden Vegetables', Decimal('0.080')),
    ]),
    ('Beef Steak', 'Mains', 18, [
        ('Beef', Decimal('0.250')),
        ('Garden Vegetables', Decimal('0.100')),
    ]),
    ('Vegetable Pasta', 'Mains', 15, [
        ('Pasta', Decimal('0.120')),
        ('Tomato', Decimal('0.080')),
        ('Garden Vegetables', Decimal('0.080')),
    ]),
    ('Chicken Biryani', 'Mains', 25, [
        ('Chicken Breast', Decimal('0.180')),
        ('Basmati Rice', Decimal('0.200')),
        ('Garden Vegetables', Decimal('0.050')),
    ]),
    ('Chocolate Fondant', 'Desserts', 12, [
        ('Dark Chocolate', Decimal('0.080')),
    ]),
    ('Seasonal Fruit Platter', 'Desserts', 6, [
        ('Seasonal Fruit', Decimal('0.250')),
    ]),
    ('Fresh Lime Soda', 'Beverages', 4, [
        ('Lime', Decimal('0.060')),
    ]),
    ('Espresso', 'Beverages', 3, [
        ('Coffee Beans', Decimal('0.018')),
    ]),
]


def _qty(value):
    return Decimal(str(value or 0))


def serialize_ingredient(ing):
    stock = _qty(ing.current_stock)
    minimum = _qty(ing.min_stock_level)
    unit_cost = _qty(ing.cost_per_unit)
    is_low = stock <= minimum
    return {
        'id': ing.id,
        'code': f'ING-{ing.id:04d}',
        'name': ing.name,
        'category': ing.category or 'General',
        'unit': ing.unit,
        'current_stock': float(stock),
        'min_stock': float(minimum),
        'min_stock_level': float(minimum),
        'max_stock': 0,
        'unit_cost': float(unit_cost),
        'cost_per_unit': float(unit_cost),
        'stock_value': float((stock * unit_cost).quantize(Decimal('0.01'))),
        'supplier': ing.supplier,
        'notes': ing.notes or '',
        'status': 'low' if is_low else 'ok',
        'is_low_stock': is_low,
    }


def recipe_cost(recipe):
    total = Decimal('0')
    lines = list(recipe.ingredients.select_related('ingredient'))
    for line in lines:
        unit_cost = _qty(line.ingredient.cost_per_unit)
        qty = _qty(line.quantity)
        line_cost = (unit_cost * qty).quantize(Decimal('0.0001'))
        if line.cost != line_cost:
            line.cost = line_cost
            line.save(update_fields=['cost'])
        total += line_cost
    servings = max(int(recipe.servings or 1), 1)
    per = (total / Decimal(servings)).quantize(Decimal('0.01'))
    total = total.quantize(Decimal('0.01'))
    if recipe.total_cost != total or recipe.cost_per_serving != per:
        recipe.total_cost = total
        recipe.cost_per_serving = per
        recipe.save(update_fields=['total_cost', 'cost_per_serving', 'updated_at'])
    return total, per, lines


def serialize_recipe(recipe, include_lines=True):
    total, per, lines = recipe_cost(recipe)
    menu_item = recipe.menu_items.filter(is_available=True).first() or recipe.menu_items.first()
    selling = _qty(menu_item.price) if menu_item else Decimal('0')
    margin = Decimal('0')
    if selling > 0:
        margin = ((selling - per) / selling * Decimal('100')).quantize(Decimal('0.1'))
    payload = {
        'id': recipe.id,
        'recipe_code': f'REC-{recipe.id:04d}',
        'name': recipe.name,
        'description': recipe.description or '',
        'category': recipe.category or 'Mains',
        'serving_size': recipe.servings or 1,
        'servings': recipe.servings or 1,
        'preparation_time': recipe.preparation_time or 0,
        'cooking_time': recipe.cooking_time or 0,
        'instructions': recipe.instructions or '',
        'total_cost': float(total),
        'cost_per_serving': float(per),
        'selling_price': float(selling),
        'profit_margin': float(margin),
        'ingredients_count': len(lines),
        'status': 'active',
        'menu_item_id': menu_item.id if menu_item else None,
        'menu_item_name': menu_item.name if menu_item else None,
    }
    if include_lines:
        payload['ingredients'] = [
            {
                'id': line.id,
                'ingredient_id': line.ingredient_id,
                'name': line.ingredient.name,
                'quantity': float(line.quantity),
                'unit': line.unit or line.ingredient.unit,
                'cost': float(line.cost or 0),
                'current_stock': float(line.ingredient.current_stock or 0),
            }
            for line in lines
        ]
    return payload


def serialize_menu(menu):
    items = list(menu.items.select_related('recipe').order_by('category', 'name'))
    return {
        'id': menu.id,
        'name': menu.name,
        'description': menu.description or '',
        'category': menu.category or '',
        'is_active': menu.is_active,
        'items_count': len(items),
        'items': [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description or '',
                'category': item.category or '',
                'price': float(item.price),
                'cost': float(item.cost or 0),
                'is_available': item.is_available,
                'recipe_id': item.recipe_id,
                'recipe_name': item.recipe.name if item.recipe_id else None,
            }
            for item in items
        ],
    }


def save_recipe_lines(recipe, lines):
    keep_ids = []
    for row in lines or []:
        ingredient_id = row.get('ingredient_id') or row.get('id')
        qty = _qty(row.get('quantity'))
        if not ingredient_id or qty <= 0:
            continue
        ingredient = Ingredient.objects.filter(tenant=recipe.tenant, id=int(ingredient_id)).first()
        if not ingredient:
            continue
        line, _created = RecipeIngredient.objects.update_or_create(
            recipe=recipe,
            ingredient=ingredient,
            defaults={
                'quantity': qty,
                'unit': row.get('unit') or ingredient.unit,
                'cost': (qty * _qty(ingredient.cost_per_unit)).quantize(Decimal('0.0001')),
            },
        )
        keep_ids.append(line.id)
    RecipeIngredient.objects.filter(recipe=recipe).exclude(id__in=keep_ids).delete()
    recipe_cost(recipe)
    if recipe.menu_items.exists():
        per = recipe.cost_per_serving or Decimal('0')
        recipe.menu_items.update(cost=per)


def apply_stock_change(ingredient, delta, movement_type, *, order=None, notes='', created_by=None):
    delta = _qty(delta)
    before = _qty(ingredient.current_stock)
    after = before + delta
    shortfall = Decimal('0')
    if after < 0:
        shortfall = -after
        after = Decimal('0')
    ingredient.current_stock = after
    ingredient.save(update_fields=['current_stock', 'updated_at'])
    IngredientStockMovement.objects.create(
        tenant=ingredient.tenant,
        ingredient=ingredient,
        movement_type=movement_type,
        quantity=delta,
        stock_before=before,
        stock_after=after,
        shortfall=shortfall,
        order=order,
        notes=(notes or '')[:255] or None,
        created_by=created_by,
    )
    return {
        'ingredient_id': ingredient.id,
        'name': ingredient.name,
        'quantity': float(delta),
        'stock_before': float(before),
        'stock_after': float(after),
        'shortfall': float(shortfall),
        'is_low_stock': after <= _qty(ingredient.min_stock_level),
    }


def deduct_recipe_stock(tenant, order, prepared_items, created_by=None):
    """Deduct BOM quantities for each sold menu item. prepared_items: (MenuItem, qty, ...)."""
    if not tenant.has_module('recipes'):
        return []
    movements = []
    with transaction.atomic():
        for row in prepared_items:
            menu_item = row[0]
            qty = int(row[1] or 0)
            if qty < 1:
                continue
            recipe = menu_item.recipe
            if not recipe:
                recipe = Recipe.objects.filter(tenant=tenant, name__iexact=menu_item.name).first()
                if recipe and not menu_item.recipe_id:
                    menu_item.recipe = recipe
                    menu_item.save(update_fields=['recipe'])
            if not recipe:
                continue
            servings = max(int(recipe.servings or 1), 1)
            for line in recipe.ingredients.select_related('ingredient'):
                needed = (_qty(line.quantity) / Decimal(servings)) * Decimal(qty)
                if needed <= 0:
                    continue
                movements.append(
                    apply_stock_change(
                        line.ingredient,
                        -needed,
                        StockMovementType.DEDUCT,
                        order=order,
                        notes=f'{order.order_number} · {menu_item.name} x{qty}',
                        created_by=created_by,
                    )
                )
    return movements


def ensure_recipe_catalog(tenant):
    """Seed kitchen stock + recipes when the module is on and empty."""
    if not tenant.has_module('recipes'):
        return
    if not Ingredient.objects.filter(tenant=tenant).exists():
        for name, category, unit, cost, stock, minimum in SEED_INGREDIENTS:
            Ingredient.objects.create(
                tenant=tenant,
                name=name,
                category=category,
                unit=unit,
                cost_per_unit=cost,
                current_stock=stock,
                min_stock_level=minimum,
            )
    ingredients = {i.name: i for i in Ingredient.objects.filter(tenant=tenant)}
    if not Recipe.objects.filter(tenant=tenant).exists():
        for name, category, prep, lines in SEED_RECIPES:
            recipe = Recipe.objects.create(
                tenant=tenant,
                name=name,
                category=category,
                servings=1,
                preparation_time=prep,
                instructions=f'House recipe for {name}.',
            )
            payload = []
            for ing_name, qty in lines:
                ing = ingredients.get(ing_name)
                if ing:
                    payload.append({'ingredient_id': ing.id, 'quantity': qty, 'unit': ing.unit})
            save_recipe_lines(recipe, payload)
            MenuItem.objects.filter(tenant=tenant, name__iexact=name, recipe__isnull=True).update(recipe=recipe)


def cost_analysis(tenant):
    recipes = list(Recipe.objects.filter(tenant=tenant).prefetch_related('ingredients__ingredient', 'menu_items'))
    rows = [serialize_recipe(r, include_lines=False) for r in recipes]
    food_cost = sum(r['cost_per_serving'] for r in rows)
    revenue = sum(r['selling_price'] for r in rows)
    low = [
        serialize_ingredient(i)
        for i in Ingredient.objects.filter(tenant=tenant)
        if _qty(i.current_stock) <= _qty(i.min_stock_level)
    ]
    stock_value = sum(
        float(_qty(i.current_stock) * _qty(i.cost_per_unit))
        for i in Ingredient.objects.filter(tenant=tenant)
    )
    return {
        'recipes': rows,
        'recipe_count': len(rows),
        'avg_food_cost': round(food_cost / len(rows), 2) if rows else 0,
        'menu_revenue': round(revenue, 2),
        'estimated_margin': round(revenue - food_cost, 2),
        'stock_value': round(stock_value, 2),
        'low_stock': low,
        'low_stock_count': len(low),
    }
