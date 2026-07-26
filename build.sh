#!/usr/bin/env bash
# exit on error
set -o errexit

# Ensure Tectonic is executable
chmod +x tectonic

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Pre-warm Tectonic cache during the build phase so it doesn't timeout in production
export XDG_CACHE_HOME=/opt/render/project/src/.cache
echo "Pre-warming Tectonic cache..."
./tectonic resume.tex || true
