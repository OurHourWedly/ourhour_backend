"""
Template 모델
"""

from django.db import models
from apps.shared.models import BaseModel


class Template(BaseModel):
    """
    청첩장 템플릿 모델
    """

    name = models.CharField(max_length=100, verbose_name="템플릿 이름")
    description = models.TextField(blank=True, verbose_name="설명")
    thumbnail_url = models.URLField(max_length=500, verbose_name="썸네일 URL")
    preview_url = models.URLField(max_length=500, blank=True, verbose_name="프리뷰 URL")
    category = models.CharField(
        max_length=50,
        choices=[
            ("MODERN", "모던"),
            ("CLASSIC", "클래식"),
            ("FLORAL", "플로럴"),
            ("MINIMAL", "미니멀"),
            ("ROMANTIC", "로맨틱"),
        ],
        verbose_name="카테고리",
    )
    is_premium = models.BooleanField(default=False, verbose_name="프리미엄 여부")
    is_active = models.BooleanField(default=True, verbose_name="사용 가능 여부")
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")

    class Meta:
        verbose_name = "템플릿"
        verbose_name_plural = "템플릿"
        db_table = "templates_template"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
