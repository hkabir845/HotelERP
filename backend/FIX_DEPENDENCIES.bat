@echo off
REM ============================================
REM Fix Backend Dependencies
REM Installs dependencies without Rust requirements
REM ============================================
cls
echo.
echo ============================================
echo   Fixing Backend Dependencies
echo ============================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies one by one to avoid Rust issues
echo.
echo Installing core dependencies (this may take a few minutes)...
echo.

REM Install uvicorn first (critical for server)
echo [1/12] Installing uvicorn...
pip install "uvicorn[standard]==0.24.0" --no-build-isolation

REM Install FastAPI
echo [2/12] Installing FastAPI...
pip install "fastapi==0.104.1" --no-build-isolation

REM Install SQLAlchemy
echo [3/12] Installing SQLAlchemy...
pip install "sqlalchemy==2.0.23" --no-build-isolation

REM Install older pydantic (doesn't require Rust)
echo [4/12] Installing Pydantic (compatible version)...
pip install "pydantic==2.4.2" --no-build-isolation

REM Install pydantic-settings
echo [5/12] Installing Pydantic Settings...
pip install "pydantic-settings==2.0.3" --no-build-isolation

REM Install python-jose
echo [6/12] Installing Python-JOSE...
pip install "python-jose[cryptography]==3.3.0" --no-build-isolation

REM Install passlib
echo [7/12] Installing Passlib...
pip install "passlib[bcrypt]==1.7.4" --no-build-isolation

REM Install python-multipart
echo [8/12] Installing Python-Multipart...
pip install "python-multipart==0.0.6" --no-build-isolation

REM Install dateutil
echo [9/12] Installing Python-Dateutil...
pip install "python-dateutil==2.8.2" --no-build-isolation

REM Install pytz
echo [10/12] Installing Pytz...
pip install "pytz==2023.3" --no-build-isolation

REM Install openpyxl
echo [11/12] Installing OpenPyXL...
pip install "openpyxl==3.1.2" --no-build-isolation

REM Install email-validator
echo [12/12] Installing Email-Validator...
pip install "email-validator==2.1.0" --no-build-isolation

echo.
echo ============================================
echo   Verifying Installation
echo ============================================
echo.

python -c "import uvicorn; print('✅ uvicorn:', uvicorn.__version__)"
python -c "import fastapi; print('✅ fastapi:', fastapi.__version__)"
python -c "import sqlalchemy; print('✅ sqlalchemy:', sqlalchemy.__version__)"
python -c "import pydantic; print('✅ pydantic:', pydantic.__version__)"

echo.
echo ============================================
echo   Dependencies Fixed!
echo ============================================
echo.
echo You can now start the backend server.
echo.
pause

