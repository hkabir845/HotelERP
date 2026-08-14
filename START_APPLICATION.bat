@echo off
REM ============================================
REM Start Hotel ERP Application
REM Starts both Backend and Frontend
REM ============================================
cls
echo.
echo ============================================
echo   Hotel ERP - Starting Application
echo ============================================
echo.

cd /d "%~dp0"

REM ============================================
REM Step 1: Clean up existing processes
REM ============================================
echo [1/5] Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   Stopping process on port 8000 - PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo   Stopping process on port 3000 - PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo   ✅ Ports cleaned
echo.

REM ============================================
REM Step 2: Check and setup Backend
REM ============================================
echo [2/5] Checking Backend...
cd backend

if not exist "venv\Scripts\python.exe" (
    echo   ❌ Backend virtual environment not found!
    echo   Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   [ERROR] Failed to create virtual environment!
        echo   Please install Python 3.8+ first.
        pause
        exit /b 1
    )
    echo   ✅ Virtual environment created
    echo   Installing dependencies (this may take 3-5 minutes)...
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt --no-build-isolation
    if errorlevel 1 (
        echo   [WARNING] Some dependencies failed, trying alternative...
        pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib python-multipart --no-build-isolation
    )
)

if not exist "app\main.py" (
    echo   [ERROR] Backend main.py not found!
    pause
    exit /b 1
)

echo   ✅ Backend ready
cd ..
echo.

REM ============================================
REM Step 3: Check and setup Frontend
REM ============================================
echo [3/5] Checking Frontend...
cd frontend

if not exist "node_modules" (
    echo   ⚠️  Frontend dependencies not installed!
    echo   Installing dependencies (this may take 3-5 minutes)...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo   Trying without --legacy-peer-deps...
        call npm install
        if errorlevel 1 (
            echo   [ERROR] Failed to install frontend dependencies!
            pause
            exit /b 1
        )
    )
    echo   ✅ Dependencies installed
) else (
    echo   ✅ Frontend dependencies ready
)

if exist ".next" (
    echo   Cleaning build cache...
    rmdir /s /q .next >nul 2>&1
)

if not exist "package.json" (
    echo   [ERROR] Frontend package.json not found!
    pause
    exit /b 1
)

echo   ✅ Frontend ready
cd ..
echo.

REM ============================================
REM Step 4: Start Backend
REM ============================================
echo [4/5] Starting Backend Server...
cd backend

REM Check SQLAlchemy compatibility
call venv\Scripts\activate.bat
python -c "import sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  Updating SQLAlchemy for compatibility...
    pip install --upgrade "sqlalchemy>=2.0.35" --no-build-isolation >nul 2>&1
)

start "Hotel ERP - Backend (Port 8000)" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && echo ============================================ && echo   Backend Server && echo   URL: http://localhost:8000 && echo   API Docs: http://localhost:8000/api/docs && echo ============================================ && echo. && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 5 /nobreak >nul
echo   ✅ Backend starting (check Backend window)
cd ..
echo.

REM ============================================
REM Step 5: Start Frontend
REM ============================================
echo [5/5] Starting Frontend Server...
cd frontend
start "Hotel ERP - Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend && echo ============================================ && echo   Frontend Server && echo   URL: http://localhost:3000 && echo ============================================ && echo. && npm run dev"
timeout /t 5 /nobreak >nul
echo   ✅ Frontend starting (check Frontend window)
cd ..

echo.
echo ============================================
echo   ✅ Application Starting!
echo ============================================
echo.
echo Two windows have opened:
echo   1. Backend (FastAPI) - Port 8000
echo   2. Frontend (Next.js) - Port 3000
echo.
echo ⏳ Please wait 30-60 seconds for both to start...
echo.
echo Then open your browser:
echo   🌐 http://localhost:3000
echo.
echo Login Credentials:
echo   Email: superadmin@admin.com
echo   Password: Admin@123
echo.
echo ============================================
echo.
echo IMPORTANT:
echo   - Keep both windows open while using the app
echo   - Backend must be running for login to work
echo   - Press CTRL+C in each window to stop
echo.
echo ============================================
pause
