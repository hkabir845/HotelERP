@echo off
REM Start Django dev server using the project virtual environment.
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run setup.bat from the project root first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
endlocal
