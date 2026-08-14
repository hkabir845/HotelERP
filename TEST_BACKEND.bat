@echo off
REM ============================================
REM Test Backend Startup
REM ============================================
cls
echo.
echo ============================================
echo   Testing Backend Startup
echo ============================================
echo.

cd /d "%~dp0backend"

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv!
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Testing imports...
python -c "import sys; sys.path.insert(0, '.'); from app.main import app; print('✅ Imports successful!')" 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Import failed! Checking dependencies...
    pip list | findstr sqlalchemy
    echo.
    echo Trying to fix SQLAlchemy...
    pip install --upgrade "sqlalchemy>=2.0.35" --no-build-isolation
    echo.
    echo Testing again...
    python -c "import sys; sys.path.insert(0, '.'); from app.main import app; print('✅ Imports successful after fix!')" 2>&1
)

echo.
echo ============================================
echo   Starting Backend Server
echo ============================================
echo.
echo If you see errors above, they need to be fixed first.
echo.
echo Starting server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

