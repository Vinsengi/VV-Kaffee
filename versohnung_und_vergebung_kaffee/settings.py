import os
from pathlib import Path
from decouple import config
from django.urls import reverse_lazy
from dotenv import load_dotenv


# Optional: only used if you set DATABASE_URL for Postgres
try:
    import dj_database_url  # pip install dj-database-url (optional)
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")   # <-- loads .env into os.environ

# ── Core settings ───────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me")  # use .env
DEBUG = config("DEBUG", default=False, cast=bool)
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ── Installed apps ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your apps
    "products",
    "orders",
    "reviews",
    "profiles.apps.ProfilesConfig",
    "cart",

    # 3rd party (add when you wire them)
    # "cloudinary_storage",  # if you use Cloudinary for static/media
    # "cloudinary",
]

# ── Middleware ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise (serves static files in production)
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "versohnung_und_vergebung_kaffee.middleware.fulfillment_redirect.FulfillmentPostLoginMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "versohnung_und_vergebung_kaffee.urls"

# ── Templates ──────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Global templates dir (you already created this)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # auto-detects app templates: <app>/templates/<app>/
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_summary",

            ],
        },
    },
]

WSGI_APPLICATION = "versohnung_und_vergebung_kaffee.wsgi.application"

# ── Database ───────────────────────────────────────────────────────────────────
# Default: SQLite for local dev
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,  # seconds
        },
    }
}

# If DATABASE_URL exists (Heroku), use it with SSL (required by Heroku Postgres)
DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )

# ── Password validation ────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalization ───────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# ── Static & Media ─────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # your global static folder
STATIC_ROOT = BASE_DIR / "staticfiles"    # collected on deploy: python manage.py collectstatic

# WhiteNoise: serve compressed static files in prod
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Stripe (from .env) ────────────────────────────────────────────────
#───────────────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")

# ── Cloudinary (from .env) ─────────────────────────────────────────────────────
# If using Cloudinary later, set CLOUDINARY_URL in .env and enable the apps above.
CLOUDINARY_URL = config("CLOUDINARY_URL", default="")

# ── Default primary key field type ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}


LOGIN_REDIRECT_URL = "/post-login/"
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "home"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Optional: timeouts & fail behavior
EMAIL_TIMEOUT = 20

SITE_NAME = "Versöhnung und Vergebung Kaffee"
SITE_URL = "http://127.0.0.1:8000"  # change in prod