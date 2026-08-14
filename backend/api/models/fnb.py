"""Food & Beverage models including Recipe Management."""
from django.db import models


class OrderStatus(models.TextChoices):
    """Order status."""

    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PREPARING = 'preparing', 'Preparing'
    READY = 'ready', 'Ready'
    SERVED = 'served', 'Served'
    CANCELLED = 'cancelled', 'Cancelled'
    COMPLETED = 'completed', 'Completed'


class OrderType(models.TextChoices):
    """Order type."""

    DINE_IN = 'dine_in', 'Dine In'
    ROOM_SERVICE = 'room_service', 'Room Service'
    TAKEAWAY = 'takeaway', 'Takeaway'
    DELIVERY = 'delivery', 'Delivery'


class TableStatus(models.TextChoices):
    """Table status."""

    AVAILABLE = 'available', 'Available'
    OCCUPIED = 'occupied', 'Occupied'
    RESERVED = 'reserved', 'Reserved'
    CLEANING = 'cleaning', 'Cleaning'


class Menu(models.Model):
    """Menu model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='menus',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    start_time = models.CharField(max_length=10, null=True, blank=True)
    end_time = models.CharField(max_length=10, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'menus'

    def __str__(self):
        return f"Menu(id={self.id}, name='{self.name}')"


class Ingredient(models.Model):
    """Ingredient model for recipes."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='ingredients',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=4)
    category = models.CharField(max_length=100, null=True, blank=True)

    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'ingredients'

    def __str__(self):
        return f"Ingredient(id={self.id}, name='{self.name}', unit='{self.unit}')"


class Recipe(models.Model):
    """Recipe model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    servings = models.IntegerField(default=1)
    preparation_time = models.IntegerField(null=True, blank=True)
    cooking_time = models.IntegerField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)

    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_serving = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'recipes'

    def __str__(self):
        return f"Recipe(id={self.id}, name='{self.name}')"


class RecipeIngredient(models.Model):
    """Recipe ingredient junction table."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='uniq_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return (
            f"RecipeIngredient(recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, quantity={self.quantity})"
        )


class MenuItem(models.Model):
    """Menu item model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='menu_items',
        db_index=True,
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',
    )

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_items',
    )

    image = models.CharField(max_length=500, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)
    revenue_center = models.CharField(max_length=100, null=True, blank=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)

    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'menu_items'

    def __str__(self):
        return f"MenuItem(id={self.id}, name='{self.name}', price={self.price})"


class Table(models.Model):
    """Restaurant table model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='tables',
        db_index=True,
    )
    table_number = models.CharField(max_length=20, db_index=True)
    capacity = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=TableStatus.choices,
        default=TableStatus.AVAILABLE,
    )
    location = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'tables'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'table_number'],
                name='uniq_table_per_tenant',
            ),
        ]

    def __str__(self):
        return f"Table(id={self.id}, table_number='{self.table_number}', status='{self.status}')"


class Order(models.Model):
    """F&B Order model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='orders',
        db_index=True,
    )
    order_number = models.CharField(max_length=50, unique=True, db_index=True)

    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    guest_name = models.CharField(max_length=200, null=True, blank=True)
    guest_phone = models.CharField(max_length=50, null=True, blank=True)
    revenue_center = models.CharField(max_length=100, null=True, blank=True)
    pos_customer = models.ForeignKey(
        'PosCustomer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    waiter = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_as_waiter',
    )
    chef = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_as_chef',
    )

    order_time = models.DateTimeField(auto_now_add=True)
    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Guest-requested serve/delivery time',
    )
    prepared_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    special_instructions = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    source = models.CharField(max_length=20, default='pos', db_index=True)
    guest_kind = models.CharField(max_length=20, default='walk_in', db_index=True)
    payment_status = models.CharField(max_length=20, default='unpaid', db_index=True)
    payment_method = models.CharField(max_length=30, null=True, blank=True)
    checkout_ref = models.CharField(max_length=64, null=True, blank=True, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created',
    )

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')"


class OrderItem(models.Model):
    """Order item model."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='order_items',
    )

    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    special_instructions = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"OrderItem(id={self.id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})"


class StockMovementType(models.TextChoices):
    RECEIVE = 'receive', 'Receive'
    DEDUCT = 'deduct', 'Order deduction'
    ADJUST = 'adjust', 'Adjustment'
    WASTE = 'waste', 'Waste'


class IngredientStockMovement(models.Model):
    """Audit log for kitchen ingredient stock changes."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='ingredient_movements',
        db_index=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='movements',
    )
    movement_type = models.CharField(max_length=20, choices=StockMovementType.choices)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    stock_before = models.DecimalField(max_digits=10, decimal_places=2)
    stock_after = models.DecimalField(max_digits=10, decimal_places=2)
    shortfall = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
    )
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingredient_movements',
    )

    class Meta:
        db_table = 'ingredient_stock_movements'

    def __str__(self):
        return (
            f"IngredientStockMovement(ingredient_id={self.ingredient_id}, "
            f"type={self.movement_type}, qty={self.quantity})"
        )
