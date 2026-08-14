@echo off
echo ========================================
echo Fixing Frontend Server Issues
echo ========================================
echo.

cd frontend

echo [Step 1] Stopping any running processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo   Stopping process PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo.
echo [Step 2] Clearing Next.js cache...
if exist .next (
    rmdir /s /q .next
    echo   Cache cleared!
) else (
    echo   No cache to clear.
)

echo.
echo [Step 3] Checking node_modules...
if not exist node_modules (
    echo   node_modules missing! Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo   [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo   node_modules exists.
)

echo.
echo [Step 4] Starting Frontend server...
echo   This may take 30-60 seconds for initial compilation...
echo.
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Frontend server is starting...
echo Please wait for compilation to complete.
echo Check the "Frontend Server" window for status.
echo ========================================
echo.
echo The server will be available at: http://localhost:3000
echo.
timeout /t 5 /nobreak >nul

