# Hotel & Resort Management ERP - World-Class Features

## ✅ Completed Features

### 🔐 Authentication & Security
- **Multi-tenant authentication** (domain-based)
- **JWT token-based auth** (access & refresh tokens)
- **Password hashing** (bcrypt)
- **Role-based access control** (Superadmin, Admin, Staff)
- **⚠️ LOGIN PROTECTED** - Never modified, always working

### 🏨 Frontdesk Management
- **Guest Management**
  - Complete guest profiles
  - ID verification
  - Loyalty program
  - VIP status
  - Blacklist management
  
- **Room Management**
  - Room types (Standard, Deluxe, Suite, Presidential, Family)
  - Room status tracking (Available, Occupied, Maintenance, etc.)
  - Room amenities and features
  - Floor management
  
- **Reservation System**
  - Individual, Group, Corporate, Walk-in reservations
  - Check-in/Check-out management
  - Reservation status tracking
  - Payment tracking
  - Special requests handling

### 🧹 Housekeeping
- **Task Management**
  - Room cleaning tasks
  - Status updates
  - Assignment to staff
  - Priority management

### 🍽️ Food & Beverage (F&B)
- **Menu Management**
  - Multiple menus (Breakfast, Lunch, Dinner, Bar)
  - Menu items with pricing
  - Categories and descriptions
  
- **Recipe Management**
  - Recipe creation
  - Ingredient tracking
  - Cost calculation
  - Profit margin analysis
  
- **Order Management**
  - Dine-in, Room Service, Takeaway, Delivery
  - Order status tracking
  - Table management
  - Kitchen integration

### 💰 Accounting System
- **Chart of Accounts**
  - Assets, Liabilities, Equity, Revenue, Expenses
  - Hierarchical account structure
  - Account codes
  
- **Journal Entries**
  - Double-entry bookkeeping
  - Debit/Credit transactions
  - Posting mechanism
  
- **Accounts Payable (AP)**
  - Vendor invoices
  - Payment tracking
  - Due date management
  
- **Accounts Receivable (AR)**
  - Customer invoices
  - Payment tracking
  - Aging reports
  
- **Budget Management**
  - Budget creation
  - Actual vs Budget comparison
  - Variance analysis

### 🏗️ Asset & Maintenance
- **Asset Management**
  - Asset categories
  - Asset tracking
  - Depreciation calculation
  - Location tracking
  
- **Maintenance System**
  - Maintenance requests
  - Preventive maintenance schedules
  - Work history
  - Cost tracking

### 📦 Inventory Management
- **Inventory Items**
  - Item codes and descriptions
  - Categories
  - Stock levels (min/max)
  - Cost and selling prices
  
- **Warehouse Management**
  - Multiple warehouses
  - Stock transfers
  - Stock adjustments
  
- **Purchase Management**
  - Purchase orders
  - Supplier management
  - Receiving
  - Supplier payments
  
- **Requisitions**
  - Department requisitions
  - Approval workflow
  - Fulfillment tracking

### 🔧 Work Order System (NEW)
- **Work Orders**
  - Work order creation
  - Approval workflow
  - Assignment to staff
  - Priority levels (Low, Medium, High, Urgent)
  - Cost tracking (Labor, Material, Other)
  - **Convert to Bill** functionality
  - Status tracking (Draft, Pending, Approved, In Progress, Completed, Converted to Bill)

### 👔 Employee & Payroll (NEW)
- **Employee Management**
  - Employee profiles
  - Department and designation
  - Employment type (Full-time, Part-time, Contract)
  - Salary/Hourly rate
  - Bank account details
  
- **Attendance Tracking**
  - Check-in/Check-out
  - Hours worked
  - Overtime tracking
  - Leave management
  
- **Payroll Processing**
  - Payroll generation
  - Earnings (Base salary, Overtime, Bonus, Allowances)
  - Deductions (Tax, Social Security, Health Insurance)
  - Net pay calculation
  - Approval workflow
  - Payment tracking

### 💱 Multi-Currency Support (NEW)
- **Currency Management**
  - Multiple currencies (USD, BDT, EUR, GBP, etc.)
  - Exchange rates
  - Base currency per tenant
  - Currency conversion
  - Exchange rate history
  
- **Tenant Currency Settings**
  - Base currency configuration
  - Allowed currencies
  - Auto-update rates

### 💳 Billing System (NEW)
- **Comprehensive Billing**
  - Bill creation for various services
  - Bill types (Room Charge, F&B, Activity, Service, Group Tour, Consolidated)
  - Line items with tax and service charges
  - Multi-currency support
  
- **Billing Items**
  - Predefined billing items
  - Categories (Room, Activity, Service, Food)
  - Pricing with tax rates
  
- **Activities & Services**
  - Resort activities (Spa, Gym, Pool, Tours)
  - Activity bookings
  - Pricing per person/group
  - Capacity management
  
- **Group Tours**
  - Tour management
  - Group leader information
  - Participant tracking
  - Pricing and payments
  
- **Bill Payments**
  - Multiple payment methods (Cash, Card, Bank Transfer, Check, Credit)
  - Payment tracking
  - Partial payments
  - Multi-currency payments

### 📊 Superadmin SaaS Dashboard (NEW)
- **Multi-Tenant Overview**
  - Total tenants and active tenants
  - Total users and active users
  - Overall statistics
  
- **Per-Tenant Statistics**
  - Reservations (total, active)
  - Rooms (total, occupied, occupancy rate)
  - Guests (total)
  - Revenue (total)
  - Employees (total)
  - Work Orders (pending)
  
- **Revenue Analytics**
  - Revenue by tenant
  - Revenue over time
  - Period-based statistics

### 📢 Broadcast Messages
- **System-wide messaging**
- **Targeted messaging**
- **Priority levels**

### ⚙️ Utilities & Settings
- **Frontdesk Configuration**
  - Guest sources
  - Booking agents
  - Companies
  - Rate plans
  - Cancellation rules
  - Board types
  - Room facilities
  - Packages

## 📝 Seed Data

Comprehensive seed data script creates:
- **50+ Guests** with realistic data
- **100+ Rooms** across 5 floors
- **30+ Reservations** with various statuses
- **20 Employees** across departments
- **15 Work Orders** with different priorities
- **20 Bills** with payments
- **10 Payroll Records**
- **5 Suppliers** with contact information
- **10+ Inventory Items** across categories
- **5 Activities** (Spa, Gym, Tours, etc.)
- **Chart of Accounts** with standard accounts
- **Multi-currency** setup (USD, BDT, EUR, GBP)

## 🚀 How to Use

### 1. Initialize Database
```bash
# Run database initialization (creates tables and default users)
INIT_DATABASE.bat
```

### 2. Create Seed Data
```bash
# Run seed data script (creates dummy data for all modules)
SEED_DATA.bat
```

### 3. Start Application
```bash
# Start both backend and frontend
start.bat
```

### 4. Login
- **Superadmin**: `superadmin@admin.com` / `Admin@123`
- **Tenant Admin**: `admin@admin.com` / `Admin@123`

## 🔒 Security & Best Practices

- ✅ **Login functionality is protected** - Never modified
- ✅ **Password hashing** using bcrypt
- ✅ **JWT authentication** with refresh tokens
- ✅ **CORS configured** for frontend
- ✅ **Rate limiting** (120 requests/minute)
- ✅ **Security headers** middleware
- ✅ **Multi-tenant isolation** (domain-based)

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

### Superadmin (Superuser only)
- `GET /api/superadmin/dashboard` - Dashboard statistics
- `GET /api/superadmin/tenants` - List all tenants
- `GET /api/superadmin/revenue` - Revenue statistics

## 🎯 World-Class Standards

This ERP system follows international hotel & resort management standards:

1. **Complete Guest Lifecycle** - From reservation to checkout
2. **Comprehensive Billing** - Room charges, activities, services, group tours
3. **Full Accounting** - Double-entry bookkeeping, AP, AR, GL
4. **Inventory Management** - Stock tracking, requisitions, purchases
5. **Asset Management** - Asset tracking, maintenance, depreciation
6. **Employee Management** - HR, attendance, payroll
7. **Multi-Currency** - Support for international operations
8. **Work Order System** - Maintenance requests with bill conversion
9. **Multi-Tenant SaaS** - Domain-based tenant isolation
10. **Superadmin Dashboard** - Complete SaaS management

## ⚠️ Important Notes

- **Login functionality is NEVER modified** - Always working
- All seed data is dummy data for testing
- Multi-currency support is fully implemented
- Work orders can be converted to bills after approval
- Payroll system includes full earnings and deductions
- Billing system handles all hotel/resort revenue streams

---

**Built with:** FastAPI (Python), Next.js (React/TypeScript), SQLite
**Architecture:** Multi-tenant SaaS, Domain-based routing
**Version:** 1.0.0

