# config/settings/development.py
# DEBUG, ALLOWED_HOSTS, SECRET_KEY, BASE_URL y LOCAL_IP se leen del .env en base.py
from .base import *

# SQLite local para desarrollo
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email a consola (no envía correos reales)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django Debug Toolbar (si está instalado)
try:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1"]
except Exception:
    pass
