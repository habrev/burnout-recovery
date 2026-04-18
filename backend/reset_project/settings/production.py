import os
import dj_database_url
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
    )
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

_use_https = os.getenv('USE_HTTPS', 'false').lower() == 'true'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if _use_https else None
SECURE_SSL_REDIRECT = _use_https
SESSION_COOKIE_SECURE = _use_https
CSRF_COOKIE_SECURE = _use_https

