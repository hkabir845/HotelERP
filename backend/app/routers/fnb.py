"""
Food & Beverage router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/fnb", tags=["F&B"])


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    price: Decimal


class OrderCreate(BaseModel):
    order_type: str  # pos, room, takeaway
    room_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[OrderItemCreate]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    notes: Optional[str] = None


@router.get("/menu-items")
async def get_menu_items(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get menu items."""
    # Mock data for now - will be replaced with actual model
    items = [
        {"id": 1, "name": "Grilled Chicken", "description": "Tender grilled chicken breast", "price": 15.99, "category": "Main Course", "image_url": None},
        {"id": 2, "name": "Caesar Salad", "description": "Fresh romaine lettuce with caesar dressing", "price": 8.99, "category": "Salad", "image_url": None},
        {"id": 3, "name": "Margherita Pizza", "description": "Classic pizza with tomato and mozzarella", "price": 12.99, "category": "Pizza", "image_url": None},
        {"id": 4, "name": "Beef Burger", "description": "Juicy beef patty with fresh vegetables", "price": 11.99, "category": "Main Course", "image_url": None},
        {"id": 5, "name": "Fish & Chips", "description": "Crispy fish with golden fries", "price": 13.99, "category": "Main Course", "image_url": None},
        {"id": 6, "name": "Chocolate Cake", "description": "Rich chocolate cake with frosting", "price": 6.99, "category": "Dessert", "image_url": None},
        {"id": 7, "name": "Coca Cola", "description": "Refreshing soft drink", "price": 2.99, "category": "Beverage", "image_url": None},
        {"id": 8, "name": "Coffee", "description": "Freshly brewed coffee", "price": 3.99, "category": "Beverage", "image_url": None},
    ]
    
    filtered = items
    if category and category != 'all':
        filtered = [item for item in filtered if item['category'].lower() == category.lower()]
    if search:
        filtered = [item for item in filtered if search.lower() in item['name'].lower() or (item.get('description') and search.lower() in item['description'].lower())]
    
    return {"items": filtered}


@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new F&B order."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Generate order number
    order_number = f"ORD-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
    
    # In a real implementation, this would create an Order record in the database
    # For now, return success
    
    return {
        "message": "Order created successfully",
        "order": {
            "id": 1,
            "order_number": order_number,
            "order_type": order_data.order_type,
            "total": float(order_data.total),
            "status": "pending"
        }
    }


@router.get("/orders")
async def get_orders(
    status: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get F&B orders."""
    # Mock data for now
    orders = [
        {
            "id": 1,
            "order_number": "ORD-2024-ABC12345",
            "order_type": "room",
            "customer_name": None,
            "customer_phone": None,
            "room_number": "101",
            "status": "preparing",
            "total": 45.97,
            "created_at": datetime.now().isoformat(),
            "items_count": 3
        },
        {
            "id": 2,
            "order_number": "ORD-2024-DEF67890",
            "order_type": "pos",
            "customer_name": "John Doe",
            "customer_phone": "+1234567890",
            "room_number": None,
            "status": "ready",
            "total": 28.98,
            "created_at": datetime.now().isoformat(),
            "items_count": 2
        }
    ]
    
    filtered = orders
    if status_filter and status_filter != 'all':
        filtered = [o for o in filtered if o['status'] == status_filter]
    if search:
        filtered = [o for o in filtered if search.lower() in o.get('order_number', '').lower() or 
                   search.lower() in (o.get('customer_name') or '').lower() or
                   search.lower() in (o.get('room_number') or '').lower()]
    
    return {"orders": filtered}


@router.get("/recipes")
async def get_recipes(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recipes."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    recipes = [
        {
            "id": 1,
            "recipe_code": "REC-001",
            "name": "Grilled Chicken",
            "category": "Main Course",
            "serving_size": 1,
            "preparation_time": 30,
            "cost_per_serving": 8.50,
            "selling_price": 15.99,
            "profit_margin": 46.8,
            "ingredients_count": 5,
            "status": "active"
        },
        {
            "id": 2,
            "recipe_code": "REC-002",
            "name": "Caesar Salad",
            "category": "Salad",
            "serving_size": 1,
            "preparation_time": 15,
            "cost_per_serving": 3.50,
            "selling_price": 8.99,
            "profit_margin": 61.0,
            "ingredients_count": 6,
            "status": "active"
        },
        {
            "id": 3,
            "recipe_code": "REC-003",
            "name": "Margherita Pizza",
            "category": "Pizza",
            "serving_size": 1,
            "preparation_time": 20,
            "cost_per_serving": 4.50,
            "selling_price": 12.99,
            "profit_margin": 65.4,
            "ingredients_count": 4,
            "status": "active"
        }
    ]
    
    filtered = recipes
    if category and category != 'all':
        filtered = [r for r in filtered if r['category'].lower() == category.lower()]
    if search:
        filtered = [r for r in filtered if search.lower() in r['name'].lower() or
                   search.lower() in r['recipe_code'].lower()]
    
    return {"recipes": filtered}


@router.get("/ingredients")
async def get_ingredients(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ingredients."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    ingredients = [
        {
            "id": 1,
            "code": "ING-001",
            "name": "Chicken Breast",
            "category": "Meat",
            "unit": "kg",
            "current_stock": 25.5,
            "min_stock": 10.0,
            "max_stock": 50.0,
            "unit_cost": 8.50,
            "supplier": "Fresh Foods Ltd",
            "status": "active"
        },
        {
            "id": 2,
            "code": "ING-002",
            "name": "Romaine Lettuce",
            "category": "Vegetables",
            "unit": "kg",
            "current_stock": 5.0,
            "min_stock": 10.0,
            "max_stock": 30.0,
            "unit_cost": 2.50,
            "supplier": "Green Market",
            "status": "active"
        },
        {
            "id": 3,
            "code": "ING-003",
            "name": "Mozzarella Cheese",
            "category": "Dairy",
            "unit": "kg",
            "current_stock": 15.0,
            "min_stock": 5.0,
            "max_stock": 25.0,
            "unit_cost": 6.00,
            "supplier": "Dairy Products Inc",
            "status": "active"
        }
    ]
    
    filtered = ingredients
    if category and category != 'all':
        filtered = [i for i in filtered if i['category'].lower() == category.lower()]
    if search:
        filtered = [i for i in filtered if search.lower() in i['name'].lower() or
                   search.lower() in i['code'].lower()]
    
    return {"ingredients": filtered}


@router.get("/sales")
async def get_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get F&B sales."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    sales = [
        {
            "id": 1,
            "order_number": "ORD-2024-ABC12345",
            "date": datetime.now().isoformat(),
            "customer_name": None,
            "room_number": "101",
            "revenue_center": "Restaurant",
            "items_count": 3,
            "subtotal": 41.97,
            "tax": 4.20,
            "discount": 0.00,
            "total": 45.97,
            "payment_method": "cash"
        },
        {
            "id": 2,
            "order_number": "ORD-2024-DEF67890",
            "date": datetime.now().isoformat(),
            "customer_name": "John Doe",
            "room_number": None,
            "revenue_center": "Bar",
            "items_count": 2,
            "subtotal": 25.98,
            "tax": 3.00,
            "discount": 0.00,
            "total": 28.98,
            "payment_method": "card"
        }
    ]
    
    filtered = sales
    if search:
        filtered = [s for s in filtered if search.lower() in s['order_number'].lower() or
                   search.lower() in (s.get('customer_name') or '').lower() or
                   search.lower() in (s.get('room_number') or '').lower()]
    
    total = len(filtered)
    total_pages = (total + limit - 1) // limit
    paginated = filtered[(page - 1) * limit:page * limit]
    
    return {
        "sales": paginated,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }
