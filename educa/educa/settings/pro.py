import os
from .base import *

DEBUG = False

ADMINS = (
    ('Antonio M', 'email@mydomain.com'),
)

ALLOWED_HOSTS = [
    '.onrender.com',
    '.educaproject.com',
    'localhost',
    '127.0.0.1',
    '*',
]

# Trusted origins for CSRF in modern Django (Required for Render HTTPS)
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://educa-platform.onrender.com',
    'https://*.educaproject.com',
    'https://educaproject.com',
]

# Trust Render reverse proxy SSL header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'educa'),
                'USER': os.environ.get('DB_USER', 'educa'),
                'PASSWORD': os.environ.get('DB_PASSWORD', '*****'),
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '5432'),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'educa'),
            'USER': os.environ.get('DB_USER', 'educa'),
            'PASSWORD': os.environ.get('DB_PASSWORD', '*****'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
