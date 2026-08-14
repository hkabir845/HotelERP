# Fixing Dependencies Without Rust

## Problem
Some Python packages (like newer versions of `pydantic-core`) require Rust to compile. If Rust is not installed, the installation fails.

## Solution

We've updated `requirements.txt` to use compatible versions that don't require Rust compilation.

### Option 1: Use the Fix Script (Recommended)

Run the fix script:
```bash
cd backend
FIX_DEPENDENCIES.bat
```

This will:
- Install all dependencies one by one
- Use `--no-build-isolation` flag to avoid Rust requirements
- Verify all packages are installed correctly

### Option 2: Manual Installation

1. Activate virtual environment:
```bash
cd backend
venv\Scripts\activate
```

2. Upgrade pip:
```bash
python -m pip install --upgrade pip
```

3. Install dependencies:
```bash
pip install -r requirements.txt --no-build-isolation
```

### Option 3: Install Pre-built Wheels

If you still have issues, install pre-built wheels:
```bash
pip install --only-binary :all: -r requirements.txt
```

## What Changed

- **pydantic**: Downgraded from `2.5.0` to `2.4.2` (pre-built wheels available)
- **pydantic-settings**: Downgraded from `2.1.0` to `2.0.3` (compatible with pydantic 2.4.2)

These versions are fully compatible with FastAPI and don't require Rust compilation.

## Verify Installation

After installation, verify:
```bash
python -c "import uvicorn; print('uvicorn:', uvicorn.__version__)"
python -c "import fastapi; print('fastapi:', fastapi.__version__)"
python -c "import pydantic; print('pydantic:', pydantic.__version__)"
```

All should print version numbers without errors.

## Alternative: Install Rust (If Needed Later)

If you need the latest pydantic features, you can install Rust:

1. Download from: https://rustup.rs/
2. Run the installer
3. Restart your terminal
4. Reinstall dependencies: `pip install -r requirements.txt`

But for now, the compatible versions work perfectly fine!

