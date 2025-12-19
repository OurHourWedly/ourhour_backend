"""
Templates 앱 시리얼라이저
"""

from rest_framework import serializers

from apps.templates.models import Template


class TemplateListSerializer(serializers.ModelSerializer):
    """템플릿 목록용 시리얼라이저"""

    class Meta:
        model = Template
        fields = ["id", "name", "thumbnail_url", "category", "is_premium", "usage_count"]


class TemplateSerializer(serializers.ModelSerializer):
    """템플릿 상세용 시리얼라이저"""

    class Meta:
        model = Template
        fields = "__all__"
        read_only_fields = ["usage_count", "created_at", "updated_at"]
