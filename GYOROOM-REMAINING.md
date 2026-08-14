# GYOROOM Turag menubar — remaining work

Source: live Turag PMS menubar copied into `frontend/lib/gyoroom-menu.ts` (Aug 2026).
Status: **228 of 228** leaf screens have real custom UI. **0 remaining.**

Interactive list: open the `pms-menubar-todo` canvas beside chat.

Do **not** count CatalogScreen / ActionScreen / ServiceRecordsPage as finished.

---

## Already done (do not rebuild)

Dashboard; Add Reservation; **Add Booking**; Reservation List; Cancel-Void-No Show; Add Registration; Registration List; Inhouse; Arrival/Departure date lists; Pending Folios; Room Rack; **Frontdesk config (17)**; **Room Rate Schedule**; **Room Type Availability Forecast**; **Room Availability Forecast**; **Agent Fund Request Create + List**; **Frontdesk reports (27 including Audit Trails)**; HK room status, amenity list, tasks, wake-up, lost & found, staff; **Guest Status Report**; **Amenity Distribution Create + Report**; **Maintenance and Block**; **Banquet (14)**; F&B New Order, Active Order List, Room-wise Active Orders, Sales List; **F&B config (8) + POS customers/due receive/statement + expenses + guest status + 5 F&B reports + Sales List [All Service]**; **Accounts voucher entry (6 types) + list**; **Chart of Accounts tree + Account + Group**; **12 accounts reports**; **Inventory stock movements (28) + Supplier List**; **Sales & Marketing / CRM (14)**; **HR (23)**; Asset register, Maintenance Request, Work Orders; **Asset Type, Category, Vendor, Vendor Contract**; Broadcast List; **Broadcast New Message, SMS Cost Report**; Manage Users; Settings; Website content editor; **Blog; Property Images, Nearby Terminal, Accepted Payment Method**; **Roles Create + List; User-Wise-Accounts-Config; Additional Configs; Activity Log; Clear Cache**.

---

## Not done — needs full finish

None. All 228 Turag menubar leaf screens have real UI wired to APIs.

### Frontdesk (0)

- [x] **Add Booking** — walk-in / confirmed booking (`/frontdesk/bookings/new`)
- [x] Room Rate Schedule
- [x] Room Type Availability Forecast
- [x] Room Availability Forecast
- [x] Config (17): Package, Room View Type, Bed Info, Room Facility, Room Group, Room Type, Room Type Special Rate, Room, Extra Charge Items, Extra Charge Group, Booking Agent, Company, Rate Plan, Cancellation Rules, Board Type, Complimentary Options, Guest Source
- [x] Agent Fund Request Create + List

### Frontdesk reports (0)

- [x] Booking, Cancel/No-Show, Arrival/Departure Summary + Details, Inhouse Summary, Expected Arr/Dep Summary + Details
- [x] Daily Sales, Booking Checklist, Pickup/Drop, Board, Add-ons, Payout, Guest, Police, Guest Due, Daily Occupied Rooms
- [x] Revenue, Manager, Night Audit, Income-Expense, Monthly Sales, Agent Commission
- [x] Daily Collection, Monthly Collection, Userwise Daily Collection
- [x] **Audit Trails Report** (`/reports/audit-trail`)

### Housekeeping (0)

- [x] Guest Status Report
- [x] Amenity Distribution Create + Report
- [x] Maintenance and Block

### Banquet (0)

- [x] Create Event, Event List, Pending Event Folios, Venue Availability Forecast
- [x] Config: Venue, External Vendor, Event Service, Individual Items, Set Menu, Sessions
- [x] Reports: Event, Service, Individual Item, Set Menu

### F&B (0)

- [x] Sales List [All Service]
- [x] POS Customers: Due Receive Create + List, Customer, Statement
- [x] Config: Revenue Center, Item, Category, Sub-Category, Unit, Token, Serve By, Take Away Agent
- [x] Expense Category, Expense Head, Expenses
- [x] Guest Status Report
- [x] Reports: Sales Sheet, Item Wise, Cancel, Userwise Collection, Expense

### Accounts (0)

- [x] Voucher entry: Cash/Bank Payment, Cash/Bank Receipt, Contra, Journal (real debit/credit posting)
- [x] Head of Account: Account + Group
- [x] Reports: Cash Book, Bank Book, General/Group Ledger, Opening Balance, Account Balance, Expense, Transaction Details, Daily Cash Sheet, Trial Balance, Profit & Loss, Balance Sheet

### Inventory (0)

- [x] Requisition Add + List
- [x] Purchase, Return, Purchase/Return List
- [x] Warehouse Transfer Add + List
- [x] Stock Adjustment Add / Remove / List
- [x] Revenue Center Consumption + Amenities Consumption
- [x] Supplier Payment Create + List, Supplier Statement
- [x] Config: Item, Category, Unit, Warehouse
- [x] Reports: Current Stock, Stock Register, Inventory, Purchase, Warehouse Transfer, Item Wise Purchase, Cost of Consumption

### Sales & Marketing (0)

- [x] Quotation, Invoice, Leads, Lead Source, Tasks
- [x] Guest Analytics, Lead Analytics
- [x] Guest Feedback; Customers Individuals + Companies
- [x] Follow-Up: Next Tasks, Comments, Checklist Report, Guest Frequency Report

### Human Resources (0)

- [x] HR Dashboard
- [x] Employees, Branches, Departments, Designations, Work Shifts
- [x] Punch In/Out, Attendance List
- [x] Leave Management, Leave Requests, Public Holidays
- [x] Salary Structure, Payroll, Bulk Payment, Payment List, Loans + Approvals, HR Settings
- [x] Reports: Monthly Attendance, Late Fine, Employee Leave, Payroll, Salary Payment

### Assets / Broadcast / Utilities (0)

- [x] Asset Type, Category, Vendor, Vendor Contract
- [x] Broadcast New Message, SMS Cost Report
- [x] Blog; Property Images, Nearby Terminal, Accepted Payment Method
- [x] Roles Create + List; User-Wise-Accounts-Config; Additional Configs; Activity Log; Clear Cache

---

## Suggested build order

1. ~~Frontdesk config + rate schedule + forecasts~~ **done**
2. ~~Accounts vouchers + reports~~ **done**
3. ~~F&B config + POS customers~~ **done**
4. ~~Inventory stock movements~~ **done**
5. ~~Frontdesk report pack (including Audit Trails)~~ **done**
6. ~~Banquet (events, folios, venue forecast, config, reports)~~ **done**
7. ~~HR + CRM~~ **done**
8. ~~Remaining HK / Assets / Utilities + leftover frontdesk (Add Booking, Agent Fund Request)~~ **done**
