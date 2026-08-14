@echo off
REM ============================================
REM Fix Frontend Dependencies
REM Installs all npm packages
REM ============================================
cls
echo.
echo ============================================
echo   Fixing Frontend Dependencies
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

echo [OK] Node.js found
node --version
echo.

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed!
    pause
    exit /b 1
)

echo [OK] npm found
npm --version
echo.

REM Clean install
echo ============================================
echo   Installing Dependencies
echo   This may take 3-5 minutes...
echo ============================================
echo.

REM Remove node_modules and package-lock.json if they exist
if exist "node_modules" (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo Removing old package-lock.json...
    del /q package-lock.json
)

if exist ".next" (
    echo Removing old .next build...
    rmdir /s /q .next
)

echo.
echo Installing packages...
echo.

REM Install dependencies
call npm install

if errorlevel 1 (
    echo.
    echo [ERROR] npm install failed!
    echo.
    echo Trying with --legacy-peer-deps...
    call npm install --legacy-peer-deps
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Installation still failed!
        echo Please check the error messages above.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo   Verifying Installation
echo ============================================
echo.

REM Verify key packages
if exist "node_modules\next" (
    echo [OK] Next.js installed
) else (
    echo [ERROR] Next.js not found!
)

if exist "node_modules\react" (
    echo [OK] React installed
) else (
    echo [ERROR] React not found!
)

if exist "node_modules\typescript" (
    echo [OK] TypeScript installed
) else (
    echo [ERROR] TypeScript not found!
)

if exist "node_modules\axios" (
    echo [OK] Axios installed
) else (
    echo [ERROR] Axios not found!
)

if exist "node_modules\zustand" (
    echo [OK] Zustand installed
) else (
    echo [ERROR] Zustand not found!
)

if exist "node_modules\tailwindcss" (
    echo [OK] Tailwind CSS installed
) else (
    echo [ERROR] Tailwind CSS not found!
)

echo.
echo ============================================
echo   Frontend Dependencies Fixed!
echo ============================================
echo.
echo ✅ Installation complete!
echo.
echo You can now start the frontend server:
echo   - Use: START_FRONTEND_DEBUG.bat (recommended - shows errors)
echo   - Or: npm run dev
echo   - Or: START_FRONTEND_ONLY.bat
echo.
echo IMPORTANT: Keep the terminal window open when running the server!
echo.
pause

