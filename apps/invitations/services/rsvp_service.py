"""
RSVP 서비스 레이어
"""

from django.db import transaction
from apps.invitations.models import RSVP, Invitation


class RSVPService:
    """RSVP 관련 비즈니스 로직 처리"""

    @staticmethod
    @transaction.atomic
    def create_or_update_rsvp(invitation: Invitation, guest_name: str, **kwargs) -> RSVP:
        """
        RSVP 생성 또는 업데이트

        같은 이름과 연락처로 이미 RSVP가 있으면 업데이트, 없으면 생성

        Args:
            invitation: Invitation 객체
            guest_name: 참석자 이름
            **kwargs: 기타 RSVP 필드들

        Returns:
            RSVP: 생성되거나 업데이트된 RSVP 객체

        Raises:
            ValueError: enable_rsvp가 False인 경우
        """
        if not invitation.enable_rsvp:
            raise ValueError("이 청첩장은 RSVP 기능이 비활성화되어 있습니다.")

        phone = kwargs.get("phone", "")

        # 같은 이름과 연락처로 기존 RSVP 찾기
        rsvp, created = RSVP.objects.get_or_create(
            invitation=invitation, guest_name=guest_name, phone=phone, defaults=kwargs
        )

        if not created:
            # 기존 RSVP 업데이트
            for key, value in kwargs.items():
                setattr(rsvp, key, value)
            rsvp.save()

        return rsvp

    @staticmethod
    def get_rsvp_statistics(invitation: Invitation) -> dict:
        """
        RSVP 통계 정보 조회

        Args:
            invitation: Invitation 객체

        Returns:
            dict: 통계 정보
        """
        rsvps = RSVP.objects.filter(invitation=invitation)

        total_count = rsvps.count()
        attending_count = rsvps.filter(attendance_status="ATTENDING").count()
        not_attending_count = rsvps.filter(attendance_status="NOT_ATTENDING").count()
        pending_count = rsvps.filter(attendance_status="PENDING").count()
        total_guests = sum(rsvp.guest_count for rsvp in rsvps.filter(attendance_status="ATTENDING"))

        return {
            "total_count": total_count,
            "attending_count": attending_count,
            "not_attending_count": not_attending_count,
            "pending_count": pending_count,
            "total_guests": total_guests,
        }
