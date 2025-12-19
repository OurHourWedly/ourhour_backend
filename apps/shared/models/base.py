"""
공통 모델 베이스 클래스
"""
from django.db import models


class BaseModel(models.Model):
    """
    모든 모델이 상속받을 기본 모델
    created_at과 updated_at 필드를 자동으로 제공
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

