"""
Soft Delete 모델
"""
from django.db import models
from django.utils import timezone
from .base import BaseModel


class SoftDeleteModel(BaseModel):
    """
    Soft Delete를 지원하는 모델
    실제로 삭제하지 않고 deleted_at 필드로 삭제 여부를 표시
    """
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='삭제일시')
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete: deleted_at을 현재 시간으로 설정"""
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def restore(self):
        """삭제된 객체 복원"""
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self) -> bool:
        """삭제 여부 확인"""
        return self.deleted_at is not None

