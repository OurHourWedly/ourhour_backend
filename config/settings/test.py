"""
테스트 환경 설정
"""
from config.settings.base import *

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# 테스트용 데이터베이스
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 테스트 실행 최적화
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# 로깅 비활성화
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# CORS 설정 완화
CORS_ALLOW_ALL_ORIGINS = True

