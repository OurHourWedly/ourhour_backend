"""
Invitations 앱 시리얼라이저
"""

from rest_framework import serializers
from apps.invitations.models import Invitation, RSVP, Guestbook
from apps.templates.serializers import TemplateListSerializer


class InvitationCreateSerializer(serializers.ModelSerializer):
    """청첩장 생성용 시리얼라이저"""

    class Meta:
        model = Invitation
        fields = [
            "template",
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
            "greeting_message",
            "ending_message",
            "background_animation",
            "background_color",
            "font_family",
            "music_url",
            "enable_rsvp",
            "enable_guestbook",
            "enable_account_transfer",
            "is_public",
            "plan_type",
            "status",
            "url_slug",
        ]
        read_only_fields = ["status", "url_slug"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        # url_slug는 서비스 레이어에서 생성
        if not validated_data.get("url_slug"):
            from apps.invitations.services.invitation_service import InvitationService

            validated_data["url_slug"] = InvitationService.generate_unique_slug()
        return super().create(validated_data)


class InvitationUpdateSerializer(serializers.ModelSerializer):
    """청첩장 수정용 시리얼라이저"""

    class Meta:
        model = Invitation
        fields = [
            "template",
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
            "greeting_message",
            "ending_message",
            "background_animation",
            "background_color",
            "font_family",
            "music_url",
            "enable_rsvp",
            "enable_guestbook",
            "enable_account_transfer",
            "is_public",
            "plan_type",
            "status",
        ]
        read_only_fields = ["url_slug"]


class InvitationSerializer(serializers.ModelSerializer):
    """청첩장 상세용 시리얼라이저"""

    template = TemplateListSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = "__all__"
        read_only_fields = ["user", "url_slug", "view_count", "created_at", "updated_at", "published_at", "status"]


class PublicInvitationSerializer(serializers.ModelSerializer):
    """공개 조회용 시리얼라이저 (민감 정보 제외)"""

    template = TemplateListSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "title",
            "url_slug",
            "template",
            "status",
            "groom_name",
            "groom_father_name",
            "groom_mother_name",
            "bride_name",
            "bride_father_name",
            "bride_mother_name",
            "wedding_date",
            "wedding_location_name",
            "wedding_location_address",
            "wedding_location_lat",
            "wedding_location_lng",
            "invitation_message",
            "greeting_message",
            "ending_message",
            "background_animation",
            "background_color",
            "font_family",
            "music_url",
            "enable_rsvp",
            "enable_guestbook",
            "view_count",
            "published_at",
        ]
        read_only_fields = ["id", "url_slug", "status", "view_count", "published_at"]


class RSVPSerializer(serializers.ModelSerializer):
    """RSVP 시리얼라이저"""

    class Meta:
        model = RSVP
        fields = [
            "id",
            "guest_name",
            "guest_count",
            "attendance_status",
            "phone",
            "message",
            "dietary_restrictions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RSVPStatisticsSerializer(serializers.Serializer):
    """RSVP 통계 시리얼라이저"""

    total_count = serializers.IntegerField()
    attending_count = serializers.IntegerField()
    not_attending_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    total_guests = serializers.IntegerField()


class GuestbookSerializer(serializers.ModelSerializer):
    """방명록 시리얼라이저"""

    class Meta:
        model = Guestbook
        fields = ["id", "author_name", "message", "is_public", "phone", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
