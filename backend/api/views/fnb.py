"""Food & Beverage endpoints — live ERP menu and orders."""
from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    Ingredient,
    IngredientStockMovement,
    Menu,
    MenuItem,
    Order,
    OrderStatus,
    Recipe,
    StockMovementType,
)
from api.services.catalog import (
    create_website_order,
    ensure_public_catalog,
    public_menu_items,
    serialize_staff_order,
)
from api.services.hotel_gl import post_fnb_sale
from api.services.recipes import (
    apply_stock_change,
    cost_analysis,
    ensure_recipe_catalog,
    save_recipe_lines,
    serialize_ingredient,
    serialize_menu,
    serialize_recipe,
)
from api.views import deny_if_no_tenant
from django.db import transaction


def _tenant(user):
    return getattr(user, 'tenant', None)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    """Get or create menu items from the tenant ERP catalog."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    if not tenant:
        return Response({'items': []})
    ensure_public_catalog(tenant)
    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('title') or data.get('name') or '').strip()
        if not name:
            return Response({'detail': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
        menu = Menu.objects.filter(tenant=tenant).first()
        if not menu:
            menu = Menu.objects.create(tenant=tenant, name='Main menu')
        row = MenuItem.objects.create(
            tenant=tenant,
            menu=menu,
            name=name,
            description=data.get('notes') or '',
            category=data.get('location') or data.get('category') or 'General',
            price=data.get('amount') or data.get('price') or 0,
        )
        return Response({
            'id': row.id,
            'name': row.name,
            'title': row.name,
            'amount': float(row.price or 0),
            'price': float(row.price or 0),
            'location': row.category or '',
            'category': row.category or '',
            'status': 'available' if row.is_available else 'unavailable',
            'notes': row.description or '',
        }, status=status.HTTP_201_CREATED)
    category = request.query_params.get('category')
    search = (request.query_params.get('search') or '').strip().lower()
    items = public_menu_items(tenant)
    if category and category != 'all':
        items = [i for i in items if (i.get('category') or '').lower() == category.lower()]
    if search:
        items = [
            i for i in items
            if search in (i.get('name') or '').lower()
            or search in (i.get('description') or '').lower()
        ]
    for item in items:
        item['image_url'] = item.get('image')
        item['title'] = item.get('name')
        item['amount'] = item.get('price') or 0
        item['location'] = item.get('category') or ''
        item['status'] = 'available' if item.get('is_available', True) else 'unavailable'
        item['notes'] = item.get('description') or ''
    return Response({'items': items})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders(request):
    """List or create F&B orders (POS and website)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    if not tenant:
        return Response({'orders': []})

    if request.method == 'POST':
        ensure_public_catalog(tenant)
        data = dict(request.data or {})
        if not data.get('customer_name'):
            data['customer_name'] = data.get('guest_name') or 'Walk-in'
        try:
            order = create_website_order(tenant, data, created_by=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'message': 'Order created successfully',
            'order': order,
            'order_number': order['order_number'],
        }, status=status.HTTP_201_CREATED)

    ensure_public_catalog(tenant)
    status_filter = request.query_params.get('status_filter') or request.query_params.get('status')
    search = (request.query_params.get('search') or '').strip()
    qs = Order.objects.filter(tenant=tenant).select_related('room', 'table').prefetch_related('items')

    active_statuses = [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY,
    ]
    if status_filter == 'active':
        qs = qs.filter(status__in=active_statuses)
    elif status_filter and status_filter != 'all':
        qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(
            Q(order_number__icontains=search)
            | Q(guest_name__icontains=search)
            | Q(guest_phone__icontains=search)
            | Q(room__room_number__icontains=search)
            | Q(table__table_number__icontains=search)
        )

    result = [serialize_staff_order(o) for o in qs.order_by('-created_at')[:200]]
    return Response({'orders': result})


ORDER_ACTIONS = {
    'confirm': OrderStatus.CONFIRMED,
    'start': OrderStatus.PREPARING,
    'prepare': OrderStatus.PREPARING,
    'ready': OrderStatus.READY,
    'serve': OrderStatus.SERVED,
    'complete': OrderStatus.COMPLETED,
    'cancel': OrderStatus.CANCELLED,
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    try:
        order = Order.objects.get(pk=pk, tenant=tenant)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    action = (request.data or {}).get('action')
    if action not in ORDER_ACTIONS:
        return Response({'detail': 'Unknown kitchen action'}, status=status.HTTP_400_BAD_REQUEST)
    order.status = ORDER_ACTIONS[action]
    if action in ('serve', 'complete'):
        order.served_at = timezone.now()
        order.completed_at = timezone.now()
    try:
        with transaction.atomic():
            order.save()
            if action in ('serve', 'complete'):
                post_fnb_sale(order, user=request.user)
    except Exception as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serialize_staff_order(order))


def _require_recipes(tenant):
    if not tenant or not tenant.has_module('recipes'):
        return Response(
            {'detail': 'Recipe Management is not enabled for this company. Ask the SaaS admin to turn on the module.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def recipes(request):
    """List or create recipes (tenant admin)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    ensure_public_catalog(tenant)
    ensure_recipe_catalog(tenant)

    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('name') or '').strip()
        if not name:
            return Response({'detail': 'Recipe name is required'}, status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.create(
            tenant=tenant,
            name=name,
            description=data.get('description') or '',
            category=data.get('category') or 'Mains',
            servings=int(data.get('servings') or data.get('serving_size') or 1),
            preparation_time=data.get('preparation_time') or 0,
            cooking_time=data.get('cooking_time') or 0,
            instructions=data.get('instructions') or '',
        )
        save_recipe_lines(recipe, data.get('ingredients') or [])
        menu_item_id = data.get('menu_item_id')
        if menu_item_id:
            MenuItem.objects.filter(tenant=tenant, id=menu_item_id).update(recipe=recipe)
        return Response({'recipe': serialize_recipe(recipe)}, status=status.HTTP_201_CREATED)

    category = request.query_params.get('category')
    search = (request.query_params.get('search') or '').strip().lower()
    qs = Recipe.objects.filter(tenant=tenant).prefetch_related('ingredients__ingredient', 'menu_items')
    if category and category != 'all':
        qs = qs.filter(category__iexact=category)
    recipes_list = [serialize_recipe(r) for r in qs.order_by('name')]
    if search:
        recipes_list = [
            r for r in recipes_list
            if search in r['name'].lower() or search in r['recipe_code'].lower()
        ]
    return Response({'recipes': recipes_list})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def recipe_detail(request, recipe_id: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    recipe = Recipe.objects.filter(tenant=tenant, id=recipe_id).first()
    if not recipe:
        return Response({'detail': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        MenuItem.objects.filter(recipe=recipe).update(recipe=None)
        recipe.delete()
        return Response({'message': 'Recipe deleted'})

    if request.method in ('PATCH', 'PUT'):
        data = request.data or {}
        for field in ('name', 'description', 'category', 'instructions'):
            if field in data:
                setattr(recipe, field, data.get(field) or '')
        if 'servings' in data or 'serving_size' in data:
            recipe.servings = int(data.get('servings') or data.get('serving_size') or 1)
        if 'preparation_time' in data:
            recipe.preparation_time = data.get('preparation_time') or 0
        if 'cooking_time' in data:
            recipe.cooking_time = data.get('cooking_time') or 0
        recipe.save()
        if 'ingredients' in data:
            save_recipe_lines(recipe, data.get('ingredients') or [])
        if 'menu_item_id' in data:
            MenuItem.objects.filter(tenant=tenant, recipe=recipe).update(recipe=None)
            if data.get('menu_item_id'):
                MenuItem.objects.filter(tenant=tenant, id=data['menu_item_id']).update(recipe=recipe)
        recipe.refresh_from_db()
    return Response({'recipe': serialize_recipe(recipe)})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ingredients(request):
    """List or create kitchen ingredients and stock."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    ensure_public_catalog(tenant)
    ensure_recipe_catalog(tenant)

    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('name') or '').strip()
        if not name:
            return Response({'detail': 'Ingredient name is required'}, status=status.HTTP_400_BAD_REQUEST)
        ing = Ingredient.objects.create(
            tenant=tenant,
            name=name,
            unit=(data.get('unit') or 'kg').strip(),
            cost_per_unit=data.get('unit_cost') or data.get('cost_per_unit') or 0,
            category=data.get('category') or 'General',
            current_stock=data.get('current_stock') or 0,
            min_stock_level=data.get('min_stock') or data.get('min_stock_level') or 0,
            supplier=data.get('supplier') or '',
            notes=data.get('notes') or '',
        )
        return Response({'ingredient': serialize_ingredient(ing)}, status=status.HTTP_201_CREATED)

    category = request.query_params.get('category')
    search = (request.query_params.get('search') or '').strip().lower()
    low_only = str(request.query_params.get('low_stock') or '') in ('1', 'true', 'yes')
    qs = Ingredient.objects.filter(tenant=tenant)
    if category and category != 'all':
        qs = qs.filter(category__iexact=category)
    items = [serialize_ingredient(i) for i in qs.order_by('name')]
    if search:
        items = [i for i in items if search in i['name'].lower() or search in i['code'].lower()]
    if low_only:
        items = [i for i in items if i['is_low_stock']]
    return Response({
        'ingredients': items,
        'low_stock_count': sum(1 for i in items if i['is_low_stock']),
    })


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def ingredient_detail(request, ingredient_id: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    ing = Ingredient.objects.filter(tenant=tenant, id=ingredient_id).first()
    if not ing:
        return Response({'detail': 'Ingredient not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        if ing.recipe_ingredients.exists():
            return Response(
                {'detail': 'This ingredient is used in a recipe. Remove it from recipes first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ing.delete()
        return Response({'message': 'Ingredient deleted'})
    data = request.data or {}
    if 'name' in data:
        ing.name = (data.get('name') or ing.name).strip()
    if 'unit' in data:
        ing.unit = data.get('unit') or ing.unit
    if 'category' in data:
        ing.category = data.get('category') or ''
    if 'unit_cost' in data or 'cost_per_unit' in data:
        ing.cost_per_unit = data.get('unit_cost') or data.get('cost_per_unit') or 0
    if 'min_stock' in data or 'min_stock_level' in data:
        ing.min_stock_level = data.get('min_stock') or data.get('min_stock_level') or 0
    if 'supplier' in data:
        ing.supplier = data.get('supplier') or ''
    if 'notes' in data:
        ing.notes = data.get('notes') or ''
    ing.save()
    return Response({'ingredient': serialize_ingredient(ing)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ingredient_stock(request, ingredient_id: int):
    """Receive, adjust, or waste kitchen stock."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    ing = Ingredient.objects.filter(tenant=tenant, id=ingredient_id).first()
    if not ing:
        return Response({'detail': 'Ingredient not found'}, status=status.HTTP_404_NOT_FOUND)
    data = request.data or {}
    try:
        quantity = Decimal(str(data.get('quantity') or 0))
    except Exception:
        return Response({'detail': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
    movement_type = (data.get('movement_type') or 'receive').strip().lower()
    if movement_type not in dict(StockMovementType.choices):
        movement_type = StockMovementType.RECEIVE
    if movement_type in (StockMovementType.WASTE, StockMovementType.DEDUCT) and quantity > 0:
        quantity = -quantity
    if movement_type == StockMovementType.RECEIVE and quantity < 0:
        quantity = -quantity
    move = apply_stock_change(
        ing,
        quantity,
        movement_type,
        notes=data.get('notes') or '',
        created_by=request.user,
    )
    ing.refresh_from_db()
    return Response({'movement': move, 'ingredient': serialize_ingredient(ing)})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menus(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    if not tenant or not tenant.has_module('fnb'):
        return Response({'detail': 'Food & Beverage is not enabled'}, status=status.HTTP_403_FORBIDDEN)
    ensure_public_catalog(tenant)
    if tenant.has_module('recipes'):
        ensure_recipe_catalog(tenant)

    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('name') or '').strip()
        if not name:
            return Response({'detail': 'Menu name is required'}, status=status.HTTP_400_BAD_REQUEST)
        menu = Menu.objects.create(
            tenant=tenant,
            name=name,
            description=data.get('description') or '',
            category=data.get('category') or '',
            is_active=True,
        )
        return Response({'menu': serialize_menu(menu)}, status=status.HTTP_201_CREATED)

    search = (request.query_params.get('search') or '').strip().lower()
    qs = Menu.objects.filter(tenant=tenant).prefetch_related('items__recipe')
    menus_list = [serialize_menu(m) for m in qs.order_by('name')]
    if search:
        menus_list = [m for m in menus_list if search in m['name'].lower()]
    return Response({'menus': menus_list})


@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def menu_item_detail(request, item_id: int):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    if not tenant:
        return Response({'detail': 'Tenant required'}, status=status.HTTP_403_FORBIDDEN)
    item = MenuItem.objects.filter(tenant=tenant, id=item_id).first()
    if not item:
        return Response({'detail': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    data = request.data or {}
    for field in ('name', 'description', 'category'):
        if field in data:
            setattr(item, field, data.get(field) or '')
    if 'price' in data:
        item.price = data.get('price') or item.price
    if 'is_available' in data:
        item.is_available = bool(data.get('is_available'))
    if 'recipe_id' in data:
        recipe_id = data.get('recipe_id') or None
        if recipe_id:
            recipe = Recipe.objects.filter(tenant=tenant, id=recipe_id).first()
            item.recipe = recipe
            if recipe and recipe.cost_per_serving is not None:
                item.cost = recipe.cost_per_serving
        else:
            item.recipe = None
    item.save()
    return Response({
        'item': {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'recipe_id': item.recipe_id,
            'is_available': item.is_available,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recipe_cost_analysis(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    ensure_recipe_catalog(tenant)
    return Response(cost_analysis(tenant))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_movements(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    blocked = _require_recipes(tenant)
    if blocked:
        return blocked
    qs = IngredientStockMovement.objects.filter(tenant=tenant).select_related('ingredient', 'order')
    ingredient_id = request.query_params.get('ingredient_id')
    if ingredient_id:
        qs = qs.filter(ingredient_id=ingredient_id)
    rows = []
    for move in qs.order_by('-created_at')[:100]:
        rows.append({
            'id': move.id,
            'ingredient': move.ingredient.name,
            'ingredient_id': move.ingredient_id,
            'movement_type': move.movement_type,
            'quantity': float(move.quantity),
            'stock_before': float(move.stock_before),
            'stock_after': float(move.stock_after),
            'shortfall': float(move.shortfall or 0),
            'order_number': move.order.order_number if move.order_id else None,
            'notes': move.notes or '',
            'created_at': move.created_at.isoformat() if move.created_at else None,
        })
    return Response({'movements': rows})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales(request):
    """F&B sales from completed/paid website and POS orders."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request.user)
    if not tenant:
        return Response({'sales': [], 'total': 0, 'page': 1, 'limit': 20, 'total_pages': 0})

    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    search = (request.query_params.get('search') or '').strip()
    all_service = str(request.query_params.get('all_service') or '').lower() in ('1', 'true', 'yes')
    date_from = (request.query_params.get('date_from') or '').strip()
    date_to = (request.query_params.get('date_to') or '').strip()
    qs = Order.objects.filter(tenant=tenant).select_related('room', 'table', 'pos_customer').prefetch_related('items')
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    if not all_service:
        qs = qs.exclude(status=OrderStatus.CANCELLED)
    if search:
        qs = qs.filter(
            Q(order_number__icontains=search)
            | Q(guest_name__icontains=search)
            | Q(room__room_number__icontains=search)
            | Q(pos_customer__name__icontains=search)
        )
    total = qs.count()
    total_pages = (total + limit - 1) // limit
    rows = qs.order_by('-created_at')[(page - 1) * limit:page * limit]
    sales_list = []
    for order in rows:
        paid = float(order.paid_amount or 0)
        total_amt = float(order.total_amount or 0)
        center = order.revenue_center or (
            'Room Service' if order.order_type == 'room_service' else 'Restaurant'
        )
        sales_list.append({
            'id': order.id,
            'order_number': order.order_number,
            'date': (order.created_at or datetime.now()).isoformat(),
            'customer_name': (order.pos_customer.name if order.pos_customer_id else None) or order.guest_name,
            'room_number': order.room.room_number if order.room_id else None,
            'revenue_center': center,
            'order_type': order.order_type,
            'source': order.source,
            'status': order.status,
            'items_count': order.items.count(),
            'subtotal': float(order.subtotal or 0),
            'tax': float(order.tax_amount or 0),
            'discount': float(order.discount or 0),
            'total': total_amt,
            'paid': paid,
            'due': max(0, round(total_amt - paid, 2)),
            'payment_method': order.payment_method or order.payment_status or 'pending',
            'payment_status': order.payment_status,
        })
    return Response({
        'sales': sales_list,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages,
    })
