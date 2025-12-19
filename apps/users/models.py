"""
User 모델
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.shared.models import BaseModel


class User(AbstractUser, BaseModel):
    """
    커스텀 User 모델
    email을 username으로 사용
    """

    email = models.EmailField(unique=True, verbose_name="이메일")
    name = models.CharField(max_length=50, verbose_name="이름")
    phone = models.CharField(max_length=20, blank=True, verbose_name="전화번호")
    provider = models.CharField(
        max_length=20, default="LOCAL", choices=[("LOCAL", "로컬"), ("KAKAO", "카카오")], verbose_name="로그인 제공자"
    )
    provider_id = models.CharField(max_length=100, blank=True, verbose_name="제공자 ID")
    role = models.CharField(
        max_length=20, default="USER", choices=[("USER", "사용자"), ("ADMIN", "관리자")], verbose_name="역할"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
        db_table = "users_user"

    def __str__(self):
        return self.email
