@echo off
REM Free port 8000 and start Hotel ERP Django backend with default superadmin login.
setlocal
set "PROJECT_ROOT=%~dp0"

echo.
echo ================================================================
echo   Fix Hotel ERP Login - Free port 8000 and start Django
echo ================================================================
echo.

echo [1/4] Stopping processes on port 8000...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('  Stopping PID ' + $_.OwningProcess); Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul

echo [2/4] Resetting superadmin credentials...
cd /d "%PROJECT_ROOT%backend"
call venv\Scripts\activate.bat
python manage.py init_db

echo [3/4] Removing frontend override (use default port 8000)...
if exist "%PROJECT_ROOT%frontend\.env.local" del "%PROJECT_ROOT%frontend\.env.local"

echo [4/4] Starting Django on http://127.0.0.1:8000 ...
start "Hotel ERP Backend" cmd /k "cd /d \"%PROJECT_ROOT%backend\" && call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo.
echo Done. Login with:
echo   Email: superadmin@admin.com
echo   Password: Admin@123
echo   Tenant subdomain: leave blank
echo.
echo Restart frontend if it is already running: npm run dev
echo.
pause
endlocal
