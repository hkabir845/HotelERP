@echo off
REM ====================================================================
REM Initial Setup Script - Hotel ERP
REM ====================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo   Hotel ERP - Initial Setup
echo ================================================================
echo.

set "PROJECT_ROOT=%~dp0"

REM Backend Setup
echo [Setting up Backend...]
cd /d "%PROJECT_ROOT%backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo Please install Python 3.8+ and add it to PATH
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo Installing Python packages...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some packages failed, trying alternative...
    pip install Django djangorestframework django-cors-headers psycopg2-binary PyJWT bcrypt python-dateutil pytz openpyxl reportlab
)

echo.
echo Initializing database...
if exist "manage.py" (
    python manage.py init_db
) else if exist "scripts\init_db.py" (
    python scripts\init_db.py
) else (
    echo [INFO] Database initialization script not found, skipping...
)

echo.
echo [Backend setup complete!]
echo.

REM Frontend Setup
echo [Setting up Frontend...]
cd /d "%PROJECT_ROOT%frontend"

if exist "package.json" (
    echo Installing Node.js packages...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        call npm install
    )
    echo.
    echo [Frontend setup complete!]
) else (
    echo [WARNING] Frontend package.json not found
)

echo.
echo ================================================================
echo   Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo   1. Run start.bat to start both servers
echo   2. Access the application at http://localhost:3000
echo   3. Login with credentials:
echo      Email: superadmin@admin.com
echo      Password: Admin@123
echo.
pause

endlocal

