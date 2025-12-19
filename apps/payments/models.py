"""
Payment 모델 (확장용)
API는 Phase 3에서 구현 예정
"""

from django.conf import settings
from django.db import models

from apps.invitations.models import Invitation
from apps.shared.models import BaseModel


class Payment(BaseModel):
    """
    결제 모델
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments", verbose_name="결제자"
    )
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name="payments", verbose_name="청첩장")
    order_id = models.CharField(max_length=100, unique=True, verbose_name="주문 ID")
    payment_key = models.CharField(max_length=200, verbose_name="결제 키")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="금액")
    plan_type = models.CharField(
        max_length=20,
        choices=[
            ("FREE", "무료"),
            ("PREMIUM", "프리미엄"),
            ("PREMIUM_PLUS", "프리미엄 플러스"),
        ],
        verbose_name="플랜 타입",
    )
    payment_method = models.CharField(max_length=50, verbose_name="결제 수단")
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "대기중"),
            ("COMPLETED", "완료"),
            ("FAILED", "실패"),
            ("REFUNDED", "환불됨"),
        ],
        default="PENDING",
        verbose_name="상태",
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="결제 일시")
    refunded_at = models.DateTimeField(null=True, blank=True, verbose_name="환불 일시")
    refund_reason = models.TextField(blank=True, verbose_name="환불 사유")

    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제"
        db_table = "payments_payment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} - {self.amount}원"
