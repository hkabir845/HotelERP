#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def _maybe_reexec_with_venv():
    """Re-run with backend/venv Python when Django is missing (Windows-friendly)."""
    backend_root = Path(__file__).resolve().parent
    venv_python = backend_root / 'venv' / 'Scripts' / 'python.exe'
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_erp.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        _maybe_reexec_with_venv()
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?\n"
            "Tip: run .\\runserver.bat or .\\venv\\Scripts\\activate first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
