@echo off
REM ============================================
REM Test Frontend Startup
REM ============================================
cls
echo.
echo ============================================
echo   Testing Frontend Startup
echo ============================================
echo.

cd /d "%~dp0frontend"

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

REM Check dependencies
if not exist "node_modules" (
    echo [WARNING] Dependencies not installed!
    echo Installing dependencies...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        call npm install
    )
) else (
    echo ✅ Dependencies installed
)

echo.
echo ============================================
echo   Starting Frontend Server
echo ============================================
echo.
call npm run dev

pause

