@echo off
echo ========================================
echo Hotel ERP - Seed Data Script
echo ========================================
echo.
echo This will create comprehensive dummy data for all modules.
echo Login credentials will NOT be modified.
echo.
pause

cd backend

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Running seed data script...
echo.

python scripts\seed_data.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Seed data created successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Error creating seed data!
    echo ========================================
)

pause

