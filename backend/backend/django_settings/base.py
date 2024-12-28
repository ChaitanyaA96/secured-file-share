### base.py ###
import os
import socket
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Determine the environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Load the appropriate .env file
if ENVIRONMENT == "dev":
    load_dotenv(BASE_DIR / ".env.dev")
elif ENVIRONMENT == "prod":
    load_dotenv(BASE_DIR / ".env.prod")
else:
    raise ValueError("Unknown DJANGO_ENV value: choose 'dev' or 'prod'")

# Security settings
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "default-secret-key")  # Use env variable in production
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",") + ["*"]

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "rest_framework",
    "rest_framework_simplejwt",
    "userauth",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

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

WSGI_APPLICATION = "backend.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Localization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = "/static/static/"
MEDIA_URL = "/static/media/"
STATIC_ROOT = "/vol/web/static"
MEDIA_ROOT = "/vol/web/media"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["core.permissions.IsUser"],
}

AUTH_USER_MODEL = "core.User"

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# CORS settings
CORS_ALLOWED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True

# Add dynamic IPs for testing on local network
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    CORS_ALLOWED_ORIGINS += [
        f"http://{local_ip}:5173",
        f"https://{local_ip}:5173",
    ]
    CSRF_TRUSTED_ORIGINS += [
        f"http://{local_ip}",
        f"https://{local_ip}",
    ]
except socket.error:
    pass

# Master key for encryption
MASTER_KEY = bytes.fromhex(os.getenv("MASTER_KEY", ""))
if not MASTER_KEY or len(MASTER_KEY) != 32:
    raise ValueError("Invalid or missing MASTER_KEY. Ensure it's a 256-bit key.")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "debug.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}