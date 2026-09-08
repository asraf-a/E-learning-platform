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
    echo "==> Loading default subjects..."
    python educa/manage.py loaddata subjects.json --settings=educa.settings.pro || true
    echo "==> Ensuring admin user exists..."
    python educa/manage.py shell --settings=educa.settings.pro << 'EOF'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@educa.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123!')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
EOF
else
    python manage.py collectstatic --no-input --settings=educa.settings.pro
    echo "==> Applying database migrations..."
    python manage.py migrate --settings=educa.settings.pro
    echo "==> Loading default subjects..."
    python manage.py loaddata subjects.json --settings=educa.settings.pro || true
    echo "==> Ensuring admin user exists..."
    python manage.py shell --settings=educa.settings.pro << 'EOF'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@educa.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123!')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
EOF
fi

echo "==> Build complete!"
