"""
Comprehensive seed data script for Hotel & Resort ERP.
Creates dummy data for all modules: guests, rooms, reservations, bills, employees, payroll, etc.
⚠️ CRITICAL: This script does NOT modify login/auth functionality.
"""
import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import *
from app.models.user import UserRole
from app.models.reservation import ReservationStatus, ReservationType
from app.models.room import RoomStatusEnum
from app.models.accounting import AccountType, TransactionType, PaymentStatus
from app.models.work_order import WorkOrderStatus, WorkOrderPriority
from app.models.employee import EmploymentStatus, PayrollStatus
from app.models.billing import BillStatus, BillType, PaymentMethod
from app.models.fnb import OrderStatus, OrderType
from app.models.inventory import RequisitionStatus, PurchaseStatus
from app.models.asset import AssetStatus, MaintenanceStatus, MaintenanceType

def get_or_create_tenant(db):
    """Get or create the default tenant."""
    tenant = db.query(Tenant).filter(Tenant.subdomain == "turag").first()
    if not tenant:
        tenant = Tenant(
            name="Turag Waterfront Resort",
            subdomain="turag",
            domain="turag.pms.gyo-room.com",
            email="admin@admin.com",
            phone="+880-1234-567890",
            address="123 Waterfront Road",
            city="Dhaka",
            state="Dhaka",
            country="Bangladesh",
            postal_code="1200",
            is_active=True,
            subscription_plan="premium"
        )
        db.add(tenant)
        db.flush()
    return tenant

def create_currencies(db, tenant):
    """Create currencies."""
    currencies_data = [
        {"code": "USD", "name": "US Dollar", "symbol": "$", "is_base": True, "exchange_rate": 1.0},
        {"code": "BDT", "name": "Bangladeshi Taka", "symbol": "৳", "is_base": False, "exchange_rate": 110.0},
        {"code": "EUR", "name": "Euro", "symbol": "€", "is_base": False, "exchange_rate": 0.92},
        {"code": "GBP", "name": "British Pound", "symbol": "£", "is_base": False, "exchange_rate": 0.79},
    ]
    
    currencies = {}
    for curr_data in currencies_data:
        currency = db.query(Currency).filter(Currency.code == curr_data["code"]).first()
        if not currency:
            currency = Currency(
                tenant_id=None,  # Global currencies
                code=curr_data["code"],
                name=curr_data["name"],
                symbol=curr_data["symbol"],
                exchange_rate=curr_data["exchange_rate"],
                is_base_currency=curr_data["is_base"],
                is_active=True
            )
            db.add(currency)
        currencies[curr_data["code"]] = currency
    
    # Set tenant base currency
    tenant_currency = db.query(TenantCurrency).filter(TenantCurrency.tenant_id == tenant.id).first()
    if not tenant_currency:
        tenant_currency = TenantCurrency(
            tenant_id=tenant.id,
            base_currency_id=currencies["USD"].id,
            auto_update_rates=False
        )
        db.add(tenant_currency)
    
    db.flush()
    return currencies

def create_room_types(db, tenant):
    """Create room types."""
    room_types_data = [
        {"name": "Standard Room", "base_rate": 50.00, "max_occupancy": 2, "amenities": "WiFi, TV, AC"},
        {"name": "Deluxe Room", "base_rate": 80.00, "max_occupancy": 2, "amenities": "WiFi, TV, AC, Mini Bar"},
        {"name": "Suite", "base_rate": 150.00, "max_occupancy": 4, "amenities": "WiFi, TV, AC, Mini Bar, Living Room"},
        {"name": "Presidential Suite", "base_rate": 300.00, "max_occupancy": 6, "amenities": "WiFi, TV, AC, Mini Bar, Living Room, Jacuzzi"},
        {"name": "Family Room", "base_rate": 120.00, "max_occupancy": 4, "amenities": "WiFi, TV, AC, Extra Beds"},
    ]
    
    room_types = []
    for rt_data in room_types_data:
        room_type = RoomType(
            tenant_id=tenant.id,
            name=rt_data["name"],
            description=f"Comfortable {rt_data['name'].lower()} with modern amenities",
            base_rate=rt_data["base_rate"],
            max_occupancy=rt_data["max_occupancy"],
            amenities=rt_data["amenities"],
            is_active=True
        )
        db.add(room_type)
        room_types.append(room_type)
    
    db.flush()
    return room_types

def create_rooms(db, tenant, room_types):
    """Create rooms."""
    rooms = []
    room_number = 101
    
    for floor in range(1, 6):
        rooms_per_floor = 20 if floor < 5 else 10
        for i in range(rooms_per_floor):
            room_type = random.choice(room_types)
            room = Room(
                tenant_id=tenant.id,
                room_number=str(room_number),
                room_type_id=room_type.id,
                floor=floor,
                status=random.choice(list(RoomStatusEnum)),
                bed_type=random.choice(["King", "Queen", "Twin", "Single"]),
                view=random.choice(["Ocean", "Garden", "City", "Pool"]),
                smoking_allowed=False,
                rack_rate=room_type.base_rate * Decimal(random.uniform(1.0, 1.3)),
                is_active=True
            )
            db.add(room)
            rooms.append(room)
            room_number += 1
    
    db.flush()
    return rooms

def create_guests(db, tenant):
    """Create guests."""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica", "William", "Ashley",
                   "James", "Amanda", "Christopher", "Melissa", "Daniel", "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]
    countries = ["USA", "UK", "Canada", "Australia", "Germany", "France", "Japan", "Bangladesh", "India", "Singapore"]
    
    guests = []
    for i in range(50):
        guest = Guest(
            tenant_id=tenant.id,
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            email=f"guest{i+1}@example.com",
            phone=f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            mobile=f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            address_line1=f"{random.randint(1,999)} Main Street",
            city=random.choice(["New York", "London", "Toronto", "Sydney", "Berlin", "Paris", "Tokyo", "Dhaka", "Mumbai", "Singapore"]),
            state=random.choice(["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]),
            country=random.choice(countries),
            postal_code=f"{random.randint(10000,99999)}",
            id_type=random.choice(["Passport", "Driver License", "National ID"]),
            id_number=f"ID{random.randint(100000,999999)}",
            date_of_birth=date(1970, 1, 1) + timedelta(days=random.randint(0, 15000)),
            nationality=random.choice(countries),
            gender=random.choice(["Male", "Female", "Other"]),
            language=random.choice(["English", "Spanish", "French", "German", "Bengali"]),
            is_vip=random.choice([True, False, False, False]),  # 25% VIP
            loyalty_points=random.randint(0, 5000),
            is_active=True
        )
        db.add(guest)
        guests.append(guest)
    
    db.flush()
    return guests

def create_reservations(db, tenant, guests, rooms):
    """Create reservations."""
    reservations = []
    for i in range(30):
        guest = random.choice(guests)
        room = random.choice(rooms)
        
        check_in = datetime.now() - timedelta(days=random.randint(0, 30))
        check_out = check_in + timedelta(days=random.randint(1, 7))
        
        room_rate = room.rack_rate or room.room_type.base_rate
        nights = (check_out - check_in).days
        total_amount = room_rate * nights
        paid_amount = total_amount * Decimal(random.uniform(0, 1))
        
        reservation = Reservation(
            tenant_id=tenant.id,
            reservation_number=f"RES-{datetime.now().year}-{str(i+1).zfill(5)}",
            guest_id=guest.id,
            room_id=room.id,
            check_in_date=check_in,
            check_out_date=check_out,
            status=random.choice(list(ReservationStatus)),
            reservation_type=random.choice(list(ReservationType)),
            room_rate=room_rate,
            total_amount=total_amount,
            paid_amount=paid_amount,
            balance=total_amount - paid_amount,
            adults=random.randint(1, 3),
            children=random.randint(0, 2),
            source=random.choice(["Online", "Phone", "Walk-in", "Travel Agent"]),
            created_by_id=1  # Assuming user ID 1 exists
        )
        db.add(reservation)
        reservations.append(reservation)
    
    db.flush()
    return reservations

def create_chart_of_accounts(db, tenant):
    """Create chart of accounts."""
    accounts_data = [
        # Assets
        {"code": "1000", "name": "Cash", "type": AccountType.ASSET, "parent": None},
        {"code": "1100", "name": "Accounts Receivable", "type": AccountType.ASSET, "parent": None},
        {"code": "1200", "name": "Inventory", "type": AccountType.ASSET, "parent": None},
        {"code": "1300", "name": "Fixed Assets", "type": AccountType.ASSET, "parent": None},
        
        # Liabilities
        {"code": "2000", "name": "Accounts Payable", "type": AccountType.LIABILITY, "parent": None},
        {"code": "2100", "name": "Accrued Expenses", "type": AccountType.LIABILITY, "parent": None},
        
        # Equity
        {"code": "3000", "name": "Owner's Equity", "type": AccountType.EQUITY, "parent": None},
        {"code": "3100", "name": "Retained Earnings", "type": AccountType.EQUITY, "parent": None},
        
        # Revenue
        {"code": "4000", "name": "Room Revenue", "type": AccountType.REVENUE, "parent": None},
        {"code": "4100", "name": "Food & Beverage Revenue", "type": AccountType.REVENUE, "parent": None},
        {"code": "4200", "name": "Activity Revenue", "type": AccountType.REVENUE, "parent": None},
        {"code": "4300", "name": "Service Revenue", "type": AccountType.REVENUE, "parent": None},
        
        # Expenses
        {"code": "5000", "name": "Cost of Goods Sold", "type": AccountType.EXPENSE, "parent": None},
        {"code": "5100", "name": "Salaries & Wages", "type": AccountType.EXPENSE, "parent": None},
        {"code": "5200", "name": "Utilities", "type": AccountType.EXPENSE, "parent": None},
        {"code": "5300", "name": "Maintenance & Repairs", "type": AccountType.EXPENSE, "parent": None},
        {"code": "5400", "name": "Marketing", "type": AccountType.EXPENSE, "parent": None},
    ]
    
    accounts = {}
    for acc_data in accounts_data:
        account = ChartOfAccount(
            tenant_id=tenant.id,
            account_code=acc_data["code"],
            account_name=acc_data["name"],
            account_type=acc_data["type"],
            parent_account_id=None,
            is_active=True,
            opening_balance=Decimal(random.uniform(0, 10000)) if acc_data["type"] in [AccountType.ASSET, AccountType.EQUITY] else Decimal(0),
            current_balance=Decimal(0)
        )
        db.add(account)
        accounts[acc_data["code"]] = account
    
    db.flush()
    return accounts

def create_suppliers(db, tenant):
    """Create suppliers."""
    suppliers_data = [
        {"name": "Fresh Food Supplies Co.", "contact": "John Supplier", "email": "john@freshfood.com", "phone": "+1-555-0101"},
        {"name": "Beverage Distributors", "contact": "Jane Distributor", "email": "jane@beverage.com", "phone": "+1-555-0102"},
        {"name": "Cleaning Supplies Inc.", "contact": "Mike Cleaner", "email": "mike@cleaning.com", "phone": "+1-555-0103"},
        {"name": "Maintenance Equipment Ltd.", "contact": "Sarah Maintainer", "email": "sarah@maintenance.com", "phone": "+1-555-0104"},
        {"name": "Linen & Textiles Co.", "contact": "David Textile", "email": "david@linen.com", "phone": "+1-555-0105"},
    ]
    
    suppliers = []
    for sup_data in suppliers_data:
        supplier = Supplier(
            tenant_id=tenant.id,
            name=sup_data["name"],
            contact_person=sup_data["contact"],
            email=sup_data["email"],
            phone=sup_data["phone"],
            address=f"{random.randint(1,999)} Supplier Street",
            is_active=True
        )
        db.add(supplier)
        suppliers.append(supplier)
    
    db.flush()
    return suppliers

def create_inventory(db, tenant, suppliers):
    """Create inventory items and categories."""
    categories_data = [
        {"name": "Food Items", "description": "Food and ingredients"},
        {"name": "Beverages", "description": "Drinks and beverages"},
        {"name": "Cleaning Supplies", "description": "Cleaning materials"},
        {"name": "Linen & Textiles", "description": "Bedding and towels"},
        {"name": "Maintenance Items", "description": "Maintenance supplies"},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = InventoryCategory(
            tenant_id=tenant.id,
            name=cat_data["name"],
            description=cat_data["description"]
        )
        db.add(category)
        categories[cat_data["name"]] = category
    
    db.flush()
    
    # Create inventory items
    items_data = [
        {"code": "FOOD-001", "name": "Rice", "category": "Food Items", "unit": "kg", "cost": 2.50, "stock": 100},
        {"code": "FOOD-002", "name": "Chicken", "category": "Food Items", "unit": "kg", "cost": 8.00, "stock": 50},
        {"code": "FOOD-003", "name": "Vegetables", "category": "Food Items", "unit": "kg", "cost": 3.00, "stock": 75},
        {"code": "BEV-001", "name": "Soft Drinks", "category": "Beverages", "unit": "case", "cost": 12.00, "stock": 30},
        {"code": "BEV-002", "name": "Juice", "category": "Beverages", "unit": "bottle", "cost": 4.00, "stock": 100},
        {"code": "CLEAN-001", "name": "Detergent", "category": "Cleaning Supplies", "unit": "bottle", "cost": 5.00, "stock": 40},
        {"code": "CLEAN-002", "name": "Bleach", "category": "Cleaning Supplies", "unit": "bottle", "cost": 3.50, "stock": 25},
        {"code": "LINEN-001", "name": "Bed Sheets", "category": "Linen & Textiles", "unit": "set", "cost": 25.00, "stock": 50},
        {"code": "LINEN-002", "name": "Towels", "category": "Linen & Textiles", "unit": "piece", "cost": 8.00, "stock": 100},
        {"code": "MAINT-001", "name": "Light Bulbs", "category": "Maintenance Items", "unit": "piece", "cost": 2.00, "stock": 200},
    ]
    
    items = []
    for item_data in items_data:
        item = InventoryItem(
            tenant_id=tenant.id,
            item_code=item_data["code"],
            name=item_data["name"],
            category_id=categories[item_data["category"]].id,
            unit=item_data["unit"],
            current_stock=item_data["stock"],
            min_stock_level=item_data["stock"] * 0.2,
            cost_price=item_data["cost"],
            supplier_id=random.choice(suppliers).id if suppliers else None,
            is_active=True
        )
        db.add(item)
        items.append(item)
    
    db.flush()
    return items, categories

def create_employees(db, tenant):
    """Create employees."""
    departments = ["Front Desk", "Housekeeping", "F&B", "Maintenance", "Management", "Security"]
    designations = ["Manager", "Supervisor", "Staff", "Assistant", "Executive"]
    
    employees = []
    for i in range(20):
        employee = Employee(
            tenant_id=tenant.id,
            employee_number=f"EMP{str(i+1).zfill(4)}",
            first_name=random.choice(["John", "Jane", "Michael", "Sarah", "David", "Emily"]),
            last_name=random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]),
            email=f"employee{i+1}@resort.com",
            phone=f"+1-555-{random.randint(1000,9999)}",
            department=random.choice(departments),
            designation=random.choice(designations),
            position=f"{random.choice(designations)} - {random.choice(departments)}",
            employment_type=random.choice(["Full-time", "Part-time", "Contract"]),
            hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
            status=EmploymentStatus.ACTIVE,
            salary=Decimal(random.uniform(2000, 8000)) if random.choice([True, False]) else None,
            hourly_rate=Decimal(random.uniform(15, 50)) if random.choice([True, False]) else None,
            pay_frequency=random.choice(["weekly", "bi-weekly", "monthly"]),
            bank_account=f"ACC{random.randint(100000,999999)}",
            bank_name=random.choice(["Bank A", "Bank B", "Bank C"]),
        )
        db.add(employee)
        employees.append(employee)
    
    db.flush()
    return employees

def create_work_orders(db, tenant, rooms, employees):
    """Create work orders."""
    work_orders = []
    for i in range(15):
        work_order = WorkOrder(
            tenant_id=tenant.id,
            work_order_number=f"WO-{datetime.now().year}-{str(i+1).zfill(5)}",
            title=random.choice(["AC Repair", "Plumbing Fix", "Electrical Work", "Painting", "Furniture Repair"]),
            description=f"Work order for {random.choice(['AC Repair', 'Plumbing Fix', 'Electrical Work', 'Painting', 'Furniture Repair'])}",
            work_type=random.choice(["Maintenance", "Repair", "Installation", "Inspection"]),
            location=f"Room {random.choice(rooms).room_number}",
            room_id=random.choice(rooms).id,
            status=random.choice(list(WorkOrderStatus)),
            priority=random.choice(list(WorkOrderPriority)),
            requested_date=date.today() - timedelta(days=random.randint(0, 30)),
            due_date=date.today() + timedelta(days=random.randint(1, 14)),
            estimated_cost=Decimal(random.uniform(50, 500)),
            actual_cost=Decimal(random.uniform(50, 500)),
            requested_by_id=1,
            assigned_to_id=random.choice(employees).id if employees else None,
        )
        db.add(work_order)
        work_orders.append(work_order)
    
    db.flush()
    return work_orders

def create_billing_items(db, tenant):
    """Create billing items."""
    categories_data = [
        {"name": "Room Charges", "type": "room"},
        {"name": "Activities", "type": "activity"},
        {"name": "Services", "type": "service"},
        {"name": "Food & Beverage", "type": "food"},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = BillingItemCategory(
            tenant_id=tenant.id,
            name=cat_data["name"],
            category_type=cat_data["type"],
            is_active=True
        )
        db.add(category)
        categories[cat_data["name"]] = category
    
    db.flush()
    
    items_data = [
        {"code": "ROOM-001", "name": "Room Charge", "category": "Room Charges", "price": 50.00, "unit": "per night"},
        {"code": "ACT-001", "name": "Spa Session", "category": "Activities", "price": 80.00, "unit": "per session"},
        {"code": "ACT-002", "name": "Gym Access", "category": "Activities", "price": 20.00, "unit": "per day"},
        {"code": "ACT-003", "name": "Pool Access", "category": "Activities", "price": 15.00, "unit": "per day"},
        {"code": "SRV-001", "name": "Laundry Service", "category": "Services", "price": 25.00, "unit": "per item"},
        {"code": "SRV-002", "name": "Room Service", "category": "Services", "price": 10.00, "unit": "per service"},
    ]
    
    items = []
    for item_data in items_data:
        item = BillingItem(
            tenant_id=tenant.id,
            item_code=item_data["code"],
            name=item_data["name"],
            category_id=categories[item_data["category"]].id,
            base_price=item_data["price"],
            unit=item_data["unit"],
            tax_rate=Decimal(10.0),
            service_charge_rate=Decimal(5.0),
            is_active=True
        )
        db.add(item)
        items.append(item)
    
    db.flush()
    return items, categories

def create_activities(db, tenant):
    """Create resort activities."""
    activities_data = [
        {"code": "SPA-001", "name": "Full Body Massage", "category": "Spa", "price_per_person": 100.00, "duration": 1.5},
        {"code": "SPA-002", "name": "Facial Treatment", "category": "Spa", "price_per_person": 60.00, "duration": 1.0},
        {"code": "FIT-001", "name": "Personal Training", "category": "Fitness", "price_per_person": 50.00, "duration": 1.0},
        {"code": "TOUR-001", "name": "City Tour", "category": "Tour", "price_per_person": 75.00, "duration": 4.0},
        {"code": "TOUR-002", "name": "Beach Excursion", "category": "Tour", "price_per_person": 90.00, "duration": 6.0},
    ]
    
    activities = []
    for act_data in activities_data:
        activity = Activity(
            tenant_id=tenant.id,
            activity_code=act_data["code"],
            name=act_data["name"],
            category=act_data["category"],
            price_per_person=act_data["price_per_person"],
            duration_hours=act_data["duration"],
            max_participants=random.randint(10, 30),
            min_participants=1,
            is_active=True
        )
        db.add(activity)
        activities.append(activity)
    
    db.flush()
    return activities

def create_bills(db, tenant, guests, reservations, billing_items, currencies):
    """Create bills."""
    bills = []
    for i in range(20):
        guest = random.choice(guests)
        reservation = random.choice(reservations) if reservations else None
        
        bill = Bill(
            tenant_id=tenant.id,
            bill_number=f"BILL-{datetime.now().year}-{str(i+1).zfill(5)}",
            guest_id=guest.id,
            reservation_id=reservation.id if reservation else None,
            room_id=reservation.room_id if reservation else None,
            bill_type=random.choice(list(BillType)),
            bill_date=date.today() - timedelta(days=random.randint(0, 30)),
            subtotal=Decimal(random.uniform(100, 1000)),
            tax_amount=Decimal(random.uniform(10, 100)),
            service_charge=Decimal(random.uniform(5, 50)),
            discount=Decimal(random.uniform(0, 50)),
            total_amount=Decimal(random.uniform(100, 1000)),
            paid_amount=Decimal(random.uniform(0, 1000)),
            balance=Decimal(random.uniform(0, 500)),
            currency_id=currencies["USD"].id,
            currency_code="USD",
            status=random.choice(list(BillStatus)),
        )
        db.add(bill)
        bills.append(bill)
    
    db.flush()
    return bills

def create_payroll(db, tenant, employees):
    """Create payroll records."""
    payrolls = []
    for i, employee in enumerate(employees[:10]):  # Create payroll for first 10 employees
        payroll = Payroll(
            tenant_id=tenant.id,
            payroll_number=f"PAY-{datetime.now().year}-{str(i+1).zfill(5)}",
            employee_id=employee.id,
            pay_period_start=date.today().replace(day=1) - timedelta(days=30),
            pay_period_end=date.today().replace(day=1) - timedelta(days=1),
            pay_date=date.today().replace(day=1),
            base_salary=employee.salary or Decimal(0),
            hours_worked=Decimal(random.uniform(160, 200)),
            hourly_rate=employee.hourly_rate or Decimal(0),
            overtime_hours=Decimal(random.uniform(0, 20)),
            overtime_rate=Decimal(random.uniform(20, 40)),
            gross_pay=Decimal(random.uniform(2000, 5000)),
            tax=Decimal(random.uniform(200, 500)),
            social_security=Decimal(random.uniform(100, 200)),
            total_deductions=Decimal(random.uniform(300, 700)),
            net_pay=Decimal(random.uniform(1500, 4000)),
            status=random.choice(list(PayrollStatus)),
        )
        db.add(payroll)
        payrolls.append(payroll)
    
    db.flush()
    return payrolls

def main():
    """Main seed data function."""
    print("=" * 60)
    print("Hotel & Resort ERP - Comprehensive Seed Data")
    print("=" * 60)
    print("\n⚠️  This script creates dummy data for all modules.")
    print("⚠️  Login/auth functionality is NOT modified.\n")
    
    db = SessionLocal()
    
    try:
        # Get or create tenant
        print("📋 Creating/Getting tenant...")
        tenant = get_or_create_tenant(db)
        print(f"✅ Tenant: {tenant.name}")
        
        # Create currencies
        print("\n💱 Creating currencies...")
        currencies = create_currencies(db, tenant)
        print(f"✅ Created {len(currencies)} currencies")
        
        # Create room types and rooms
        print("\n🏨 Creating room types and rooms...")
        room_types = create_room_types(db, tenant)
        print(f"✅ Created {len(room_types)} room types")
        rooms = create_rooms(db, tenant, room_types)
        print(f"✅ Created {len(rooms)} rooms")
        
        # Create guests
        print("\n👥 Creating guests...")
        guests = create_guests(db, tenant)
        print(f"✅ Created {len(guests)} guests")
        
        # Create reservations
        print("\n📅 Creating reservations...")
        reservations = create_reservations(db, tenant, guests, rooms)
        print(f"✅ Created {len(reservations)} reservations")
        
        # Create chart of accounts
        print("\n📊 Creating chart of accounts...")
        accounts = create_chart_of_accounts(db, tenant)
        print(f"✅ Created {len(accounts)} accounts")
        
        # Create suppliers
        print("\n🏪 Creating suppliers...")
        suppliers = create_suppliers(db, tenant)
        print(f"✅ Created {len(suppliers)} suppliers")
        
        # Create inventory
        print("\n📦 Creating inventory...")
        items, categories = create_inventory(db, tenant, suppliers)
        print(f"✅ Created {len(categories)} categories and {len(items)} items")
        
        # Create employees
        print("\n👔 Creating employees...")
        employees = create_employees(db, tenant)
        print(f"✅ Created {len(employees)} employees")
        
        # Create work orders
        print("\n🔧 Creating work orders...")
        work_orders = create_work_orders(db, tenant, rooms, employees)
        print(f"✅ Created {len(work_orders)} work orders")
        
        # Create billing items
        print("\n💰 Creating billing items...")
        billing_items, billing_categories = create_billing_items(db, tenant)
        print(f"✅ Created {len(billing_categories)} categories and {len(billing_items)} items")
        
        # Create activities
        print("\n🎯 Creating activities...")
        activities = create_activities(db, tenant)
        print(f"✅ Created {len(activities)} activities")
        
        # Create bills
        print("\n🧾 Creating bills...")
        bills = create_bills(db, tenant, guests, reservations, billing_items, currencies)
        print(f"✅ Created {len(bills)} bills")
        
        # Create payroll
        print("\n💵 Creating payroll records...")
        payrolls = create_payroll(db, tenant, employees)
        print(f"✅ Created {len(payrolls)} payroll records")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ SEED DATA CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Currencies: {len(currencies)}")
        print(f"  - Room Types: {len(room_types)}")
        print(f"  - Rooms: {len(rooms)}")
        print(f"  - Guests: {len(guests)}")
        print(f"  - Reservations: {len(reservations)}")
        print(f"  - Chart of Accounts: {len(accounts)}")
        print(f"  - Suppliers: {len(suppliers)}")
        print(f"  - Inventory Items: {len(items)}")
        print(f"  - Employees: {len(employees)}")
        print(f"  - Work Orders: {len(work_orders)}")
        print(f"  - Billing Items: {len(billing_items)}")
        print(f"  - Activities: {len(activities)}")
        print(f"  - Bills: {len(bills)}")
        print(f"  - Payroll Records: {len(payrolls)}")
        print("\n⚠️  Login credentials remain unchanged!")
        print("   Superadmin: superadmin@admin.com / Admin@123")
        print("   Tenant Admin: admin@admin.com / Admin@123")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

