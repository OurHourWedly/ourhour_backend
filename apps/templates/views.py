"""
Templates 앱 뷰
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from apps.templates.models import Template
from apps.templates.serializers import TemplateSerializer, TemplateListSerializer


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Template ViewSet
    list, retrieve만 제공
    """
    queryset = Template.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_premium']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'usage_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TemplateListSerializer
        return TemplateSerializer

