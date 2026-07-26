#!/usr/bin/env bash
# exit on error
set -o errexit

# Ensure Tectonic is executable
chmod +x tectonic

# Install uv for blazing fast dependency resolution
pip install uv
uv pip install --system -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
