"""
Templates 앱 뷰
"""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.invitations.models import Invitation
from apps.invitations.serializers import PublicInvitationSerializer
from apps.templates.models import Template, UserTemplate
from apps.templates.serializers import (
    TemplateCreateSerializer,
    TemplateListSerializer,
    TemplateSerializer,
    TemplateUpdateSerializer,
    UserTemplateSerializer,
)


class TemplateViewSet(viewsets.ModelViewSet):
    """
    Template ViewSet
    CRUD 제공 (생성/수정/삭제는 인증 필요)
    """

    queryset = Template.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_premium", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "usage_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """list와 retrieve는 활성화된 템플릿만 조회"""
        if self.action in ["list", "retrieve"]:
            return Template.objects.filter(is_active=True)
        return Template.objects.all()

    def get_permissions(self):
        """생성/수정/삭제는 인증 필요, 조회는 모두 허용"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "list":
            return TemplateListSerializer
        elif self.action == "create":
            return TemplateCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TemplateUpdateSerializer
        return TemplateSerializer

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def preview(self, request, pk=None):
        """
        템플릿 샘플 invitation 조회

        GET /api/v1/templates/{id}/preview/
        인증 불필요
        """
        template = self.get_object()

        if not template.sample_slug:
            return Response({"error": "이 템플릿에는 샘플이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        sample_invitation = get_object_or_404(Invitation, url_slug=template.sample_slug, status="PUBLISHED")

        serializer = PublicInvitationSerializer(sample_invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTemplateViewSet(viewsets.ModelViewSet):
    """
    UserTemplate ViewSet
    사용자 템플릿 CRUD 및 적용 기능
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserTemplateSerializer

    def get_queryset(self):
        """현재 사용자의 템플릿만 조회"""
        return UserTemplate.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        템플릿을 Invitation에 적용

        POST /api/v1/templates/my/{id}/apply/
        body: {"invitation_id": 1}
        """
        user_template = self.get_object()
        invitation_id = request.data.get("invitation_id")

        if not invitation_id:
            return Response({"error": "invitation_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(id=invitation_id, user=request.user)
        except Invitation.DoesNotExist:
            return Response({"error": "청첩장을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 템플릿 데이터를 Invitation에 적용
        from apps.templates.services.template_service import UserTemplateService

        updated_invitation = UserTemplateService.apply_template_to_invitation(user_template, invitation)

        from apps.invitations.serializers import InvitationSerializer

        serializer = InvitationSerializer(updated_invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)
