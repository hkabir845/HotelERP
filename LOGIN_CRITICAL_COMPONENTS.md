# 🔐 LOGIN SYSTEM - CRITICAL COMPONENTS

## ⚠️ DO NOT MODIFY THESE WITHOUT TESTING LOGIN FIRST

This document lists all critical components that MUST work for login to function.

---

## ✅ Current Working Configuration

### 1. Database Users
- **Superadmin**: `superadmin@admin.com` / `Admin@123`
- **Tenant Admin**: `admin@admin.com` / `Admin@123`
- **Location**: `backend/hotel_erp.db`
- **Table**: `users`

### 2. Password Hashing
- **Method**: Direct `bcrypt` (NOT passlib)
- **File**: `backend/app/auth/security.py`
- **Functions**:
  - `get_password_hash(password)` - Creates hash
  - `verify_password(plain, hashed)` - Verifies password
- **⚠️ CRITICAL**: Do NOT change back to passlib - it causes compatibility issues

### 3. Authentication Endpoint
- **Route**: `POST /api/auth/login`
- **File**: `backend/app/routers/auth.py`
- **Function**: `login(login_data: UserLogin, request: Request, db: Session)`
- **Key Logic**:
  - Accepts username/email and password
  - For superadmin: `tenant_id = None` (no tenant check)
  - Calls `authenticate_user()` to verify credentials
  - Returns JWT tokens on success

### 4. Authentication Function
- **File**: `backend/app/auth/security.py`
- **Function**: `authenticate_user(db, username, password, tenant_id)`
- **Key Logic**:
  - Finds user by username OR email
  - Checks if user is active
  - **Superusers bypass tenant check** (critical!)
  - Verifies password using bcrypt
  - Returns User object or None

### 5. CORS Configuration
- **File**: `backend/app/main.py` and `backend/app/config.py`
- **Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Credentials**: `allow_credentials=True`
- **Methods**: GET, POST, PUT, DELETE, OPTIONS, PATCH

---

## 🚫 DO NOT CHANGE

### ❌ Password Hashing
- **DO NOT** switch back to `passlib`
- **DO NOT** change bcrypt implementation
- **DO NOT** modify `get_password_hash()` or `verify_password()`

### ❌ Tenant Logic for Superadmin
- **DO NOT** add tenant requirement for superadmin login
- **DO NOT** call `get_current_tenant()` in login endpoint
- **DO NOT** enforce tenant_id for superusers in `authenticate_user()`

### ❌ Login Endpoint Structure
- **DO NOT** change the login endpoint signature
- **DO NOT** remove the `tenant_id = None` logic for superadmin
- **DO NOT** modify the JWT token creation

### ❌ CORS Settings
- **DO NOT** remove `localhost:3000` from allowed origins
- **DO NOT** set `allow_credentials=False`
- **DO NOT** remove Authorization header from allowed headers

---

## ✅ How to Test Login

### Quick Test
```bash
cd backend
venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); from app.database import SessionLocal; from app.models.user import User; from app.auth.security import verify_password; db = SessionLocal(); user = db.query(User).filter(User.email == 'superadmin@admin.com').first(); result = verify_password('Admin@123', user.hashed_password) if user else False; print('Login works!' if result else 'Login broken!'); db.close()"
```

### Full Test
1. Start backend: `start.bat`
2. Open: http://localhost:3000
3. Login with: `superadmin@admin.com` / `Admin@123`
4. Should redirect to `/home`

---

## 🔧 If Login Breaks

### Step 1: Check Users Exist
```bash
cd backend
python -c "import sqlite3; conn = sqlite3.connect('hotel_erp.db'); cursor = conn.cursor(); cursor.execute('SELECT username, email FROM users'); print(cursor.fetchall())"
```

### Step 2: Reinitialize Database (if needed)
```bash
cd backend
venv\Scripts\python.exe scripts\init_db.py
```

### Step 3: Verify Password Hashing
- Check `backend/app/auth/security.py` uses `bcrypt` directly
- NOT `passlib`

### Step 4: Check CORS
- Verify `backend/app/config.py` has `localhost:3000` in `CORS_ORIGINS`
- Verify `backend/app/main.py` has `allow_credentials=True`

---

## 📝 Current Working Credentials

- **Superadmin**: `superadmin@admin.com` / `Admin@123`
- **Tenant Admin**: `admin@admin.com` / `Admin@123` (subdomain: `turag`)

---

## ⚠️ REMEMBER

**LOGIN MUST ALWAYS WORK. DO NOT BREAK IT.**

If you need to modify authentication:
1. Test login BEFORE making changes
2. Test login AFTER making changes
3. If login breaks, REVERT immediately
4. Document any changes here

---

**Last Verified**: 2025-12-10
**Status**: ✅ WORKING

