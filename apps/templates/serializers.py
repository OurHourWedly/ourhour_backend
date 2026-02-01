"""
Templates 앱 시리얼라이저
"""

from rest_framework import serializers

from apps.templates.models import Template, UserTemplate


class TemplateListSerializer(serializers.ModelSerializer):
    """템플릿 목록용 시리얼라이저"""

    class Meta:
        model = Template
        fields = ["id", "name", "thumbnail_url", "category", "is_premium", "usage_count", "sample_slug"]
        read_only_fields = ["sample_slug"]


class TemplateSerializer(serializers.ModelSerializer):
    """템플릿 상세용 시리얼라이저"""

    class Meta:
        model = Template
        fields = "__all__"
        read_only_fields = ["usage_count", "sample_slug", "created_at", "updated_at"]


class TemplateCreateSerializer(serializers.ModelSerializer):
    """템플릿 생성용 시리얼라이저"""

    class Meta:
        model = Template
        fields = ["name", "description", "thumbnail_url", "preview_url", "category", "is_premium", "is_active"]
        read_only_fields = []


class TemplateUpdateSerializer(serializers.ModelSerializer):
    """템플릿 수정용 시리얼라이저"""

    class Meta:
        model = Template
        fields = ["name", "description", "thumbnail_url", "preview_url", "category", "is_premium", "is_active"]
        read_only_fields = []


class UserTemplateSerializer(serializers.ModelSerializer):
    """사용자 템플릿 시리얼라이저"""

    class Meta:
        model = UserTemplate
        fields = ["id", "name", "template_data", "is_default", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        # 기본 템플릿이 하나만 있도록 처리
        if validated_data.get("is_default"):
            UserTemplate.objects.filter(user=validated_data["user"], is_default=True).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 기본 템플릿이 하나만 있도록 처리
        if validated_data.get("is_default") and not instance.is_default:
            UserTemplate.objects.filter(user=instance.user, is_default=True).update(is_default=False)
        return super().update(instance, validated_data)
