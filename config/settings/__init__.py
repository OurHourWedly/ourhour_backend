"""
Django Settings 모듈

환경 변수 DJANGO_ENV에 따라 적절한 설정 파일을 로드합니다.
- production: prod.py
- staging: staging.py
- dev: dev.py
- test: test.py
- local (기본값): local.py
"""

import os

ENVIRONMENT = os.getenv("DJANGO_ENV", "local").lower()

if ENVIRONMENT == "production":
    from config.settings.prod import *
elif ENVIRONMENT == "staging":
    from config.settings.staging import *
elif ENVIRONMENT == "dev":
    from config.settings.dev import *
elif ENVIRONMENT == "test":
    from config.settings.test import *
else:
    from config.settings.local import *

# 로컬 개발 환경에서 ALLOWED_HOSTS 최종 확정 설정
# 모든 설정 파일 로드 후 맨 마지막에 설정하여 어떤 값이든 덮어쓰기
if ENVIRONMENT == "local" or ENVIRONMENT not in ["production", "staging", "dev", "test"]:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
