@echo off
REM ====================================================================
REM Verify Login System is Working
REM ====================================================================

echo.
echo ================================================================
echo   Verifying Login System
echo ================================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [1/3] Checking users in database...
python -c "import sqlite3; conn = sqlite3.connect('hotel_erp.db'); cursor = conn.cursor(); cursor.execute('SELECT username, email, is_active FROM users'); users = cursor.fetchall(); print(f'Users found: {len(users)}'); [print(f'  - {u[0]} ({u[1]}) - Active: {bool(u[2])}') for u in users]; conn.close()"

if errorlevel 1 (
    echo [ERROR] Failed to check users!
    pause
    exit /b 1
)

echo.
echo [2/3] Testing password verification...
python -c "import sys; sys.path.insert(0, '.'); from app.database import SessionLocal; from app.models.user import User; from app.auth.security import verify_password; db = SessionLocal(); user = db.query(User).filter(User.email == 'superadmin@admin.com').first(); result = verify_password('Admin@123', user.hashed_password) if user else False; print('Password verification: ' + ('PASS' if result else 'FAIL')); db.close()"

if errorlevel 1 (
    echo [ERROR] Password verification failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Checking authentication function...
python -c "import sys; sys.path.insert(0, '.'); from app.database import SessionLocal; from app.models.user import User; from app.auth.security import authenticate_user; import asyncio; db = SessionLocal(); async def test(): result = await authenticate_user(db, 'superadmin@admin.com', 'Admin@123', None); print('Authentication: ' + ('PASS' if result else 'FAIL')); asyncio.run(test()); db.close()"

if errorlevel 1 (
    echo [ERROR] Authentication function failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   ✅ Login System Verification Complete
echo ================================================================
echo.
echo All checks passed! Login should work.
echo.
pause

