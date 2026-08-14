@echo off
REM ====================================================================
REM Start Backend and Frontend Servers - Hotel ERP
REM ====================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo   Starting Hotel ERP System
echo ================================================================
echo.

REM Get the directory where this batch file is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and add it to your system PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js and add it to your system PATH
    pause
    exit /b 1
)

REM ====================================================================
REM Clean up existing processes
REM ====================================================================

echo [Cleaning up ports...]
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('  Stopping process on port 8000 - PID: ' + $_.OwningProcess); Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('  Stopping process on port 3000 - PID: ' + $_.OwningProcess); Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul
echo [OK] Ports cleaned
echo.

REM ====================================================================
REM Start Backend Server
REM ====================================================================

echo [Starting Backend Server...]
cd /d "%PROJECT_ROOT%backend"

if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    pause
    exit /b 1
)

if not exist "manage.py" (
    echo [ERROR] manage.py not found in backend directory!
    pause
    exit /b 1
)

REM Create a temporary batch file to run the backend server
set "BACKEND_SCRIPT=%TEMP%\hotel_backend_%RANDOM%.bat"
(
    echo @echo off
    echo cd /d "%PROJECT_ROOT%backend"
    echo call venv\Scripts\activate.bat
    echo echo.
    echo echo ================================================================
    echo echo   Backend Server - Django
    echo echo ================================================================
    echo echo API: http://127.0.0.1:8000/api/
    echo echo Admin: http://127.0.0.1:8000/admin/
    echo echo.
    echo python manage.py init_db
    echo python manage.py runserver 0.0.0.0:8000
    echo echo.
    echo echo [Backend Server] Press any key to close...
    echo pause ^>nul
) > "%BACKEND_SCRIPT%"

start "Backend Server" cmd /k ""%BACKEND_SCRIPT%""

echo [OK] Backend server starting on http://127.0.0.1:8000
echo.

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM ====================================================================
REM Start Frontend Server
REM ====================================================================

echo [Starting Frontend Server...]
cd /d "%PROJECT_ROOT%frontend"

if not exist "package.json" (
    echo [ERROR] Frontend package.json not found!
    echo Please ensure the frontend directory is set up correctly.
    pause
    exit /b 1
)

REM Check if node_modules exists, if not, install
if not exist "node_modules" (
    echo [WARNING] Node modules not found. Installing...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        call npm install
        if errorlevel 1 (
            echo [ERROR] Failed to install Node.js packages
            pause
            exit /b 1
        )
    )
)

REM Clean build cache
if exist ".next" (
    rmdir /s /q .next >nul 2>&1
)

REM Create a temporary batch file to run the frontend server
set "FRONTEND_SCRIPT=%TEMP%\hotel_frontend_%RANDOM%.bat"
(
    echo @echo off
    echo cd /d "%PROJECT_ROOT%frontend"
    echo echo.
    echo echo ================================================================
    echo echo   Frontend Server - Next.js
    echo echo ================================================================
    echo echo App: http://localhost:3000/
    echo echo.
    echo call npm run dev
    echo echo.
    echo echo [Frontend Server] Press any key to close...
    echo pause ^>nul
) > "%FRONTEND_SCRIPT%"

start "Frontend Server" cmd /k ""%FRONTEND_SCRIPT%""

echo [OK] Frontend server starting on http://localhost:3000
echo.

REM Wait for servers to initialize
echo [Waiting for servers to initialize...]
timeout /t 5 /nobreak >nul

REM ====================================================================
REM Show Status and Open Browser
REM ====================================================================

echo.
echo ================================================================
echo   Servers Started Successfully!
echo ================================================================
echo.
echo Access Points:
echo   - Frontend App:  http://localhost:3000/
echo   - Backend API:   http://127.0.0.1:8000/api/
echo   - Django Admin:  http://127.0.0.1:8000/admin/
echo.
echo Server Windows:
echo   - "Backend Server" (Django)
echo   - "Frontend Server" (Next.js)
echo.
echo To stop servers, close the respective windows.
echo.
echo Login Credentials:
echo   - Email: superadmin@admin.com
echo   - Password: Admin@123
echo.
echo Opening application in browser...
timeout /t 2 /nobreak >nul
start "" "http://localhost:3000/"

echo.
echo Press any key to close this window (servers will keep running)...
pause >nul

REM Cleanup temporary scripts
if exist "%BACKEND_SCRIPT%" del "%BACKEND_SCRIPT%"
if exist "%FRONTEND_SCRIPT%" del "%FRONTEND_SCRIPT%"

endlocal

