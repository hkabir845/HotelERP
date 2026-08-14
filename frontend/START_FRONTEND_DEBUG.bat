@echo off
REM ============================================
REM Start Frontend Server with Debug Output
REM This keeps the window open to show errors
REM ============================================
cls
echo.
echo ============================================
echo   Starting Frontend Server (Debug Mode)
echo ============================================
echo.

cd /d "%~dp0"

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo [ERROR] node_modules not found!
    echo.
    echo Installing dependencies first...
    echo This will take 3-5 minutes...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed!
        echo Trying with --legacy-peer-deps...
        call npm install --legacy-peer-deps
        if errorlevel 1 (
            echo.
            echo [ERROR] Installation failed!
            echo Please run: FIX_FRONTEND.bat
            pause
            exit /b 1
        )
    )
    echo.
    echo [OK] Dependencies installed
    echo.
)

REM Clear .next folder to avoid build errors
if exist ".next" (
    echo Clearing old build cache...
    rmdir /s /q .next
)

echo.
echo ============================================
echo   Starting Frontend Server
echo   URL: http://localhost:3000
echo ============================================
echo.
echo IMPORTANT: Keep this window open!
echo The server will show errors here if any occur.
echo.
echo Press CTRL+C to stop the server
echo.
echo ============================================
echo.

REM Start the server (this will keep the window open)
call npm run dev

REM If we get here, the server stopped
echo.
echo ============================================
echo   Server Stopped
echo ============================================
echo.
pause

