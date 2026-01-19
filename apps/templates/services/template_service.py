"""
Templates 앱 서비스 레이어
비즈니스 로직을 처리하는 레이어
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.invitations.models import Invitation
from apps.invitations.services.invitation_service import InvitationService
from apps.templates.models import Template

User = get_user_model()


class TemplateService:
    """Template 관련 비즈니스 로직 처리"""

    @staticmethod
    def get_or_create_sample_user():
        """
        샘플 invitation 소유자 계정 조회 또는 생성

        Returns:
            User: 샘플 계정 User 객체
        """
        sample_email = "sample@ourhour.com"
        user, created = User.objects.get_or_create(
            email=sample_email,
            defaults={
                "username": sample_email,
                "name": "샘플 계정",
                "role": "ADMIN",
            },
        )
        return user

    @staticmethod
    def generate_sample_slug(template_id: int) -> str:
        """
        샘플 invitation용 고유한 slug 생성

        Args:
            template_id: 템플릿 ID

        Returns:
            str: 고유한 slug 문자열
        """
        max_attempts = 10
        for _ in range(max_attempts):
            random_part = uuid.uuid4().hex[:8]
            slug = f"sample-{template_id}-{random_part}"

            # 중복 체크
            if not Invitation.objects.filter(url_slug=slug).exists():
                return slug

        return f"sample-{template_id}-{int(timezone.now().timestamp())}"

    @staticmethod
    def create_sample_invitation(template: Template, update_existing: bool = False) -> Invitation:
        """
        템플릿에 대한 샘플 invitation 생성

        Args:
            template: Template 객체
            update_existing: 기존 샘플이 있으면 업데이트할지 여부

        Returns:
            Invitation: 생성된 샘플 Invitation 객체
        """
        # 이미 샘플이 있는 경우
        if template.sample_slug:
            existing_invitation = Invitation.objects.filter(url_slug=template.sample_slug).first()
            if existing_invitation:
                if not update_existing:
                    return existing_invitation
                # 기존 샘플 삭제
                existing_invitation.delete()

        # 샘플 계정 조회 또는 생성
        sample_user = TemplateService.get_or_create_sample_user()

        # 샘플 slug 생성
        sample_slug = TemplateService.generate_sample_slug(template.id)

        # 샘플 invitation 생성
        sample_invitation = Invitation.objects.create(
            user=sample_user,
            template=template,
            title=f"[샘플] {template.name}",
            url_slug=sample_slug,
            groom_name="홍길동",
            groom_father_name="홍아버지",
            groom_mother_name="홍어머니",
            groom_phone="010-1234-5678",
            bride_name="김영희",
            bride_father_name="김아버지",
            bride_mother_name="김어머니",
            bride_phone="010-9876-5432",
            wedding_date=timezone.now() + timedelta(days=30),
            wedding_location_name="샘플 예식장",
            wedding_location_address="서울특별시 강남구 샘플로 123",
            wedding_location_lat=37.5665,
            wedding_location_lng=126.9780,
            invitation_message="저희 두 사람이 사랑으로 하나가 되어 새로운 인생을 시작하려 합니다.\n귀한 시간 내어 축하해 주시면 더없는 기쁨이겠습니다.",
            greeting_message="소중한 분들을 초대합니다",
            ending_message="참석 여부를 알려주시면 더욱 감사하겠습니다.",
            background_color="#FFFFFF",
            font_family="default",
            enable_rsvp=True,
            enable_guestbook=True,
            enable_account_transfer=False,
            is_public=True,
            status="PUBLISHED",
            published_at=timezone.now(),
        )

        # Template에 sample_slug 저장
        template.sample_slug = sample_slug
        template.save(update_fields=["sample_slug"])

        return sample_invitation
