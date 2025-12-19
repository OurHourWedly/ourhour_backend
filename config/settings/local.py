"""
로컬 개발 환경 설정
"""

from config.settings.base import *

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Database (MySQL for local development)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "ourhour_local"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

# 개발 전용 앱 추가
INSTALLED_APPS += [
    "django_extensions",
    "debug_toolbar",
]

# 개발 전용 미들웨어 추가
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# CORS 설정 (개발 환경)
CORS_ALLOW_ALL_ORIGINS = True

# 로깅 설정 (개발 환경 - 상세)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
