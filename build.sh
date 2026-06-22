#!/usr/bin/env bash
# Render build step: install, collect static, migrate, seed.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed   # idempotent — safe on every deploy

# Optional: auto-create an admin on first deploy if these env vars are set
# (DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD). Safe to leave unset.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --no-input || true
fi
