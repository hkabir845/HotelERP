@echo off
REM ====================================================================
REM Initialize Database - Create Default Users
REM ====================================================================

echo.
echo ================================================================
echo   Initializing Database
echo ================================================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Running database initialization...
call venv\Scripts\activate.bat
python scripts\init_db.py

if errorlevel 1 (
    echo.
    echo [ERROR] Database initialization failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   Database Initialized Successfully!
echo ================================================================
echo.
echo Default Credentials:
echo   Superadmin: superadmin@admin.com / Admin@123
echo   Tenant Admin: admin@admin.com / Admin@123
echo.
pause

