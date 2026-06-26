"""Core Django settings for the VMS API."""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0",
).split(",")


# Installed apps are grouped by framework, third-party packages, then local apps.
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",

    # Local apps
    "authentication",
    "organization",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "vms_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "vms_api.wsgi.application"


# Database configuration comes from `DATABASE_URL` so the project stays twelve-factor friendly.
DATABASE_URL = config(
    "DATABASE_URL",
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
)

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=DATABASE_URL.startswith("postgres"),
    )
}


# Use the custom user model everywhere in the project.
AUTH_USER_MODEL = "authentication.User"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Yangon"
USE_I18N = True
USE_TZ = True


# Static assets are served separately from uploaded media files.
STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CORS is intentionally restricted to the frontend origins used during development.
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
).split(",")

CORS_ALLOW_CREDENTIALS = True


# CSRF trusted origins should match any browser-based clients that submit forms.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default=(
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:8000,"
        "http://127.0.0.1:8000"
    ),
).split(",")


# DRF uses JWT auth and a shared OpenAPI schema definition.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# OpenAPI / Swagger metadata shown in the documentation UI.
SPECTACULAR_SETTINGS = {
    "TITLE": "VMS API",
    "DESCRIPTION": (
        "Volunteer Management System API.\n\n"
        "Most endpoints return a standard envelope:\n"
        "`{ success, message, data, errors }`.\n\n"
        "JWT login and refresh endpoints return `{ access, refresh }` directly."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "CONTACT": {
        "name": "Htet Arkar",
        "email": "htetarkarlevi@gmail.com",
    },
    "LICENSE": {
        "name": "MIT License",
    },
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
}


# JWT lifetimes balance UX with token revocation safety.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}


# Email settings are sourced from the environment to support multiple deployments.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
