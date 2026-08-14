"""
Legacy database initialization script.
Delegates to Django management command: python manage.py init_db
"""
import os
import subprocess
import sys

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANAGE_PY = os.path.join(BACKEND_ROOT, 'manage.py')


def main():
    if not os.path.isfile(MANAGE_PY):
        print('[ERROR] manage.py not found. Run setup from the backend directory.')
        sys.exit(1)
    subprocess.run([sys.executable, MANAGE_PY, 'init_db'], cwd=BACKEND_ROOT, check=True)


if __name__ == '__main__':
    main()
