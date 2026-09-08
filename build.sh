#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static assets..."
if [ -f "educa/manage.py" ]; then
    python educa/manage.py collectstatic --no-input --settings=educa.settings.pro
    echo "==> Applying database migrations..."
    python educa/manage.py migrate --settings=educa.settings.pro
else
    python manage.py collectstatic --no-input --settings=educa.settings.pro
    echo "==> Applying database migrations..."
    python manage.py migrate --settings=educa.settings.pro
fi

echo "==> Build complete!"
