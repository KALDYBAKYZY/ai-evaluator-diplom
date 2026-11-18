import os
from pathlib import Path


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "1" if default else "0").lower() in {"1", "true", "yes"}


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:5173").split(",") if o]

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CANVAS_URL = os.getenv("CANVAS_URL", "http://localhost:3000")
LTI_PRIVATE_KEY_PATH = Path(os.getenv("LTI_PRIVATE_KEY_PATH", BASE_DIR.parent / "infra" / "lti" / "keys" / "private.key"))
LTI_PUBLIC_KEY_PATH = Path(os.getenv("LTI_PUBLIC_KEY_PATH", BASE_DIR.parent / "infra" / "lti" / "keys" / "public.key"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.accounts",
    "apps.projects",
    "apps.rubrics",
    "apps.evaluations",
    "apps.pitch",
    "apps.audit",
    "apps.lti",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "config.middleware.FrameAncestorsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

if os.getenv("DB_ENGINE", "postgres") == "sqlite":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "evaluator"),
            "USER": os.getenv("POSTGRES_USER", "evaluator"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "evaluator"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if env_bool("USE_S3"):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": os.getenv("S3_BUCKET", "evaluator-files"),
                "endpoint_url": os.getenv("S3_ENDPOINT_URL") or None,
                "access_key": os.getenv("S3_ACCESS_KEY"),
                "secret_key": os.getenv("S3_SECRET_KEY"),
                "default_acl": "private",
                "querystring_auth": True,
                "querystring_expire": 600,
            },
        },
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024

SESSION_COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
SESSION_COOKIE_SECURE = env_bool("COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"user": os.getenv("API_RATE_LIMIT", "120/min")},
}

CELERY_BROKER_URL = REDIS_URL or "memory://"
CELERY_RESULT_BACKEND = None
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_EAGER", not REDIS_URL)
CELERY_TIMEZONE = TIME_ZONE
