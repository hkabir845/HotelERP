@echo off
REM ============================================
REM Check Frontend for Common Errors
REM ============================================
cls
echo.
echo ============================================
echo   Frontend Error Checker
echo ============================================
echo.

cd /d "%~dp0"

echo [1/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found!
    echo    Install from: https://nodejs.org/
) else (
    node --version
    echo ✅ Node.js OK
)
echo.

echo [2/6] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found!
) else (
    npm --version
    echo ✅ npm OK
)
echo.

echo [3/6] Checking node_modules...
if exist "node_modules" (
    echo ✅ node_modules exists
    if exist "node_modules\next" (
        echo ✅ Next.js installed
    ) else (
        echo ❌ Next.js not found in node_modules
    )
    if exist "node_modules\react" (
        echo ✅ React installed
    ) else (
        echo ❌ React not found in node_modules
    )
) else (
    echo ❌ node_modules MISSING!
    echo    Run: npm install
)
echo.

echo [4/6] Checking package.json...
if exist "package.json" (
    echo ✅ package.json exists
) else (
    echo ❌ package.json MISSING!
)
echo.

echo [5/6] Checking TypeScript config...
if exist "tsconfig.json" (
    echo ✅ tsconfig.json exists
) else (
    echo ❌ tsconfig.json MISSING!
)
echo.

echo [6/6] Checking for syntax errors...
if exist "node_modules" (
    echo Running TypeScript check...
    npx tsc --noEmit --skipLibCheck 2>&1 | findstr /C:"error" /C:"Error" /C:"ERROR"
    if errorlevel 1 (
        echo ✅ No TypeScript errors found
    ) else (
        echo ⚠️  TypeScript errors found above
    )
) else (
    echo ⏭️  Skipping (node_modules not found)
)
echo.

echo ============================================
echo   Check Complete
echo ============================================
echo.
echo If you see errors above, fix them before starting.
echo.
pause

