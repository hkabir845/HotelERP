"""
Food & Beverage models including Recipe Management.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class OrderType(str, enum.Enum):
    """Order type."""
    DINE_IN = "dine_in"
    ROOM_SERVICE = "room_service"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class TableStatus(str, enum.Enum):
    """Table status."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"


class Menu(Base):
    """Menu model."""
    
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # Breakfast, Lunch, Dinner, Bar, etc.
    is_active = Column(Boolean, default=True)
    
    start_time = Column(String(10), nullable=True)  # HH:MM format
    end_time = Column(String(10), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Menu(id={self.id}, name='{self.name}')>"


class MenuItem(Base):
    """Menu item model."""
    
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    menu = relationship("Menu", back_populates="items")
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Appetizer, Main Course, Dessert, etc.
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=True)  # Cost from recipe
    profit_margin = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Recipe
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    recipe = relationship("Recipe", back_populates="menu_items")
    
    # Image
    image = Column(String(500), nullable=True)
    
    # Status
    is_available = Column(Boolean, default=True)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_spicy = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    order_items = relationship("OrderItem", back_populates="menu_item")
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"


class Ingredient(Base):
    """Ingredient model for recipes."""
    
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    unit = Column(String(50), nullable=False)  # kg, liter, piece, etc.
    cost_per_unit = Column(Numeric(10, 4), nullable=False)
    category = Column(String(100), nullable=True)  # Vegetable, Meat, Spice, etc.
    
    # Inventory
    current_stock = Column(Numeric(10, 2), default=0)
    min_stock_level = Column(Numeric(10, 2), default=0)
    supplier = Column(String(200), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', unit='{self.unit}')>"


class Recipe(Base):
    """Recipe model."""
    
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Recipe details
    servings = Column(Integer, default=1)
    preparation_time = Column(Integer, nullable=True)  # minutes
    cooking_time = Column(Integer, nullable=True)  # minutes
    instructions = Column(Text, nullable=True)  # Step-by-step instructions
    
    # Costing
    total_cost = Column(Numeric(10, 2), nullable=True)  # Calculated from ingredients
    cost_per_serving = Column(Numeric(10, 2), nullable=True)
    
    # Image
    image = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    menu_items = relationship("MenuItem", back_populates="recipe")
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}')>"


class RecipeIngredient(Base):
    """Recipe ingredient junction table."""
    
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    
    quantity = Column(Numeric(10, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    cost = Column(Numeric(10, 4), nullable=True)  # Calculated: quantity * ingredient.cost_per_unit
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")
    
    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity})>"


class Table(Base):
    """Restaurant table model."""
    
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    table_number = Column(String(20), nullable=False, unique=True, index=True)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(TableStatus), default=TableStatus.AVAILABLE)
    location = Column(String(100), nullable=True)  # Indoor, Outdoor, VIP, etc.
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    orders = relationship("Order", back_populates="table")
    
    def __repr__(self):
        return f"<Table(id={self.id}, table_number='{self.table_number}', status='{self.status}')>"


class Order(Base):
    """F&B Order model."""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Table (for dine-in)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    table = relationship("Table", back_populates="orders")
    
    # Room (for room service)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    
    # Guest
    guest_name = Column(String(200), nullable=True)
    guest_phone = Column(String(50), nullable=True)
    
    # Pricing
    subtotal = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    service_charge = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    
    # Staff
    waiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    waiter = relationship("User", foreign_keys=[waiter_id])
    chef_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    chef = relationship("User", foreign_keys=[chef_id])
    
    # Timing
    order_time = Column(DateTime(timezone=True), server_default=func.now())
    prepared_at = Column(DateTime(timezone=True), nullable=True)
    served_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    special_instructions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """Order item model."""
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="items")
    
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    menu_item = relationship("MenuItem", back_populates="order_items")
    
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    special_instructions = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, preparing, ready, served
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"

