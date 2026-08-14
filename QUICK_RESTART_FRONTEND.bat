@echo off
echo ========================================
echo Quick Frontend Restart
echo ========================================
echo.

cd frontend

echo Stopping processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo Clearing cache...
if exist .next rmdir /s /q .next >nul 2>&1

echo Starting server...
start "Frontend" cmd /k "npm run dev"

echo.
echo Server starting... Please wait 30-60 seconds for compilation.
echo Then open: http://localhost:3000
echo.
timeout /t 2

