"""
Templates 앱 뷰
"""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.invitations.models import Invitation
from apps.invitations.serializers import PublicInvitationSerializer
from apps.templates.models import Template
from apps.templates.serializers import TemplateListSerializer, TemplateSerializer


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Template ViewSet
    list, retrieve만 제공
    """

    queryset = Template.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_premium"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "usage_count"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return TemplateListSerializer
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
