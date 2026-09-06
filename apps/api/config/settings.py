"""Django sozlamalari — RankWant API.

Stack: ADR-0003 (Django 5.2 LTS + DRF) · Auth: ADR-0008 (session + PAT).
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, str(default)).lower() in {"1", "true", "yes"}


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-not-for-production")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [h for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "core",
    "problems",
    "judging",
    "contests",
    "ratings",
    "qvant",
    "notifications",
    "blog",
    "content",
    "classroom",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

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
            ],
        },
    },
]

# ── Ma'lumotlar bazasi ────────────────────────────────────────────────
if env("DATABASE_URL"):
    import urllib.parse as _url

    _p = _url.urlparse(env("DATABASE_URL"))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _p.path.lstrip("/"),
            "USER": _p.username or "",
            "PASSWORD": _p.password or "",
            "HOST": _p.hostname or "",
            "PORT": str(_p.port or ""),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── i18n — PRD P0-7: UI uz/ru/en ─────────────────────────────────────
LANGUAGE_CODE = "uz"
LANGUAGES = [("uz", "O'zbekcha"), ("ru", "Русский"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Session — ADR-0008 ───────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG

REDIS_URL = env("REDIS_URL", "redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
    if env("REDIS_URL")
    else {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}

CORS_ALLOWED_ORIGINS = [
    o for o in env("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o
]
CORS_ALLOW_CREDENTIALS = True

# ── DRF ──────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    # PAT BIRINCHI: DRF `WWW-Authenticate` sarlavhasini birinchi
    # autentifikatordan oladi. SessionAuthentication uni bermaydi, shuning
    # uchun u birinchi bo'lsa yaroqsiz token 401 emas, 403 qaytaradi.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.auth.ApiTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.errors.exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # ADR-0008 rate limitlari
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "user": "300/min", "submit": "6/min"},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "RankWant API",
    "DESCRIPTION": "Sport dasturlash va olimpiada platformasi — ochiq REST API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
}

# ── Judge — ADR-0004 ─────────────────────────────────────────────────
JUDGE_PROVIDER = env("JUDGE_PROVIDER", "redis")
JUDGE_JOBS_KEY = "rankwant:judge:jobs"
JUDGE_RESULTS_KEY = "rankwant:judge:results"

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_EAGER", False)

# Davriy tasklar. Judge natijalari tez-tez o'qiladi, chunki foydalanuvchi
# verdictni kutib turadi (NFR: p50 < 5s) — navbat bo'sh bo'lsa BRPOP
# darhol qaytadi, ya'ni bu qimmat emas.
CELERY_BEAT_SCHEDULE = {
    "drain-judge-results": {
        "task": "judging.drain_results",
        "schedule": 2.0,
    },
    "finalize-due-contests": {
        "task": "contests.finalize_due",
        "schedule": 60.0,
    },
    "announce-published-posts": {
        "task": "blog.announce_published",
        "schedule": 300.0,
    },
    # Activity 30 kunlik siljuvchi oyna — hech kim faol bo'lmasa ham
    # kunlik pasayishi kerak, aks holda reyting muzlab qoladi.
    "decay-activity-ratings": {
        "task": "ratings.refresh_activity",
        "schedule": 3600.0,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
}
