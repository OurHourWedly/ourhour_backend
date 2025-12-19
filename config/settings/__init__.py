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
