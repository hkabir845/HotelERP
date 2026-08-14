#!/usr/bin/env bash
# First-time / update setup on sas@192.168.68.105
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Backend venv + deps"
cd "$ROOT/backend"
python3 -m venv .venv
./.venv/bin/pip install -U pip wheel
./.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  SECRET=$(./.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))')
  cat > .env <<EOF
DEBUG=False
USE_SQLITE=true
SECRET_KEY=${SECRET}
PLATFORM_ROOT_DOMAIN=sascorporationbd.com
ALLOWED_HOSTS=*
EOF
  echo "Wrote backend/.env (sqlite)"
fi

mkdir -p uploads staticfiles
./.venv/bin/python manage.py migrate --noinput
./.venv/bin/python manage.py collectstatic --noinput
./.venv/bin/python manage.py init_db || true

echo "==> Frontend deps + build"
cd "$ROOT/frontend"
if [ ! -f .env.production.local ]; then
  cat > .env.production.local <<'EOF'
DJANGO_API_URL=http://127.0.0.1:116
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_PLATFORM_ROOT_DOMAIN=sascorporationbd.com
EOF
fi
npm ci || npm install
DJANGO_API_URL=http://127.0.0.1:116 \
NEXT_PUBLIC_API_URL=/api \
NEXT_PUBLIC_PLATFORM_ROOT_DOMAIN=sascorporationbd.com \
npm run build

echo "==> Install user systemd units"
mkdir -p "$HOME/.config/systemd/user"
cp -f "$ROOT/deploy/systemd/"*.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now hotelerp-backend.service hotelerp-frontend.service hotelerp-cf-proxy.service

sleep 3
echo "==> Health checks"
curl -s -o /dev/null -w "API :116 %{http_code}\n" --max-time 5 http://127.0.0.1:116/api/public/resolve?host=turag.sascorporationbd.com || true
curl -s -o /dev/null -w "FE  :117 %{http_code}\n" --max-time 5 http://127.0.0.1:117/ || true
curl -s -o /dev/null -w "NGX :118 %{http_code}\n" --max-time 5 http://127.0.0.1:118/ || true
echo "Done. Public: https://turag.sascorporationbd.com"
