@echo off
echo ========================================
echo Restarting Frontend Server
echo ========================================
echo.

cd frontend

echo Stopping any running Next.js processes...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *next*" 2>nul

echo.
echo Clearing Next.js cache...
if exist .next (
    rmdir /s /q .next
    echo Cache cleared!
) else (
    echo No cache to clear.
)

echo.
echo Installing dependencies (if needed)...
call npm install

echo.
echo Starting Frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Frontend server is starting...
echo Please wait for compilation to complete.
echo ========================================
timeout /t 3 >nul

