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


class UserTemplateService:
    """UserTemplate 관련 비즈니스 로직 처리"""

    @staticmethod
    def apply_template_to_invitation(user_template, invitation):
        """
        사용자 템플릿을 Invitation에 적용

        Args:
            user_template: UserTemplate 객체
            invitation: Invitation 객체

        Returns:
            Invitation: 업데이트된 Invitation 객체
        """
        template_data = user_template.template_data

        # 템플릿 데이터의 필드들을 Invitation에 적용
        # JSONField에 저장된 데이터를 Invitation 필드에 매핑
        update_fields = []
        for field_name, field_value in template_data.items():
            if hasattr(invitation, field_name):
                setattr(invitation, field_name, field_value)
                update_fields.append(field_name)

        # 교통수단 데이터가 있으면 처리
        if "transportations" in template_data:
            from apps.invitations.models import Transportation

            # 기존 교통수단 삭제
            Transportation.objects.filter(invitation=invitation).delete()

            # 새 교통수단 생성
            for idx, transport_data in enumerate(template_data["transportations"]):
                Transportation.objects.create(
                    invitation=invitation,
                    transport_type=transport_data.get("transport_type"),
                    content=transport_data.get("content", ""),
                    order=transport_data.get("order", idx),
                )

        if update_fields:
            invitation.save(update_fields=update_fields)

        return invitation

    @staticmethod
    def create_template_from_invitation(invitation, name, is_default=False):
        """
        Invitation에서 사용자 템플릿 생성

        Args:
            invitation: Invitation 객체
            name: 템플릿 이름
            is_default: 기본 템플릿 여부

        Returns:
            UserTemplate: 생성된 UserTemplate 객체
        """
        from apps.invitations.models import Transportation
        from apps.templates.models import UserTemplate

        # Invitation의 모든 필드를 템플릿 데이터로 변환
        template_data = {}
        invitation_fields = [
            "title",
            "groom_name",
            "groom_father_name",
            "groom_mother_name",
            "groom_phone",
            "bride_name",
            "bride_father_name",
            "bride_mother_name",
            "bride_phone",
            "wedding_date",
            "wedding_location_name",
            "wedding_location_address",
            "wedding_location_lat",
            "wedding_location_lng",
            "invitation_message",
            "greeting_title",
            "greeting_subtitle",
            "greeting_message",
            "greeting_name_display_type",
            "greeting_name_manual",
            "ending_message",
            "photo_urls",
            "photo_frame_type",
            "photo_effect",
            "show_calendar",
            "show_dday",
            "show_countdown",
            "show_map",
            "lock_map",
            "show_navigation",
            "background_animation",
            "background_color",
            "background_texture",
            "background_effect",
            "font_family",
            "font_color",
            "font_weight",
            "music_url",
            "prevent_zoom",
            "scroll_animation",
            "enable_rsvp",
            "enable_guestbook",
            "enable_account_transfer",
            "is_public",
        ]

        for field_name in invitation_fields:
            if hasattr(invitation, field_name):
                value = getattr(invitation, field_name)
                # DateTimeField는 ISO 형식으로 변환
                if hasattr(value, "isoformat"):
                    template_data[field_name] = value.isoformat()
                else:
                    template_data[field_name] = value

        # 교통수단 데이터 추가
        transportations = Transportation.objects.filter(invitation=invitation).order_by("order")
        template_data["transportations"] = [
            {
                "transport_type": t.transport_type,
                "content": t.content,
                "order": t.order,
            }
            for t in transportations
        ]

        # 기본 템플릿이 하나만 있도록 처리
        if is_default:
            UserTemplate.objects.filter(user=invitation.user, is_default=True).update(is_default=False)

        # UserTemplate 생성
        user_template = UserTemplate.objects.create(
            user=invitation.user,
            name=name,
            template_data=template_data,
            is_default=is_default,
        )

        return user_template
