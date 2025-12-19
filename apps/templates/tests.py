"""
Templates 앱 테스트
"""

import pytest
from rest_framework import status
from apps.templates.models import Template


@pytest.fixture
def template():
    """테스트용 템플릿 fixture"""
    return Template.objects.create(
        name="테스트 템플릿",
        description="테스트용 템플릿입니다",
        thumbnail_url="https://example.com/thumb.jpg",
        category="MODERN",
        is_premium=False,
        is_active=True,
    )


@pytest.fixture
def premium_template():
    """프리미엄 템플릿 fixture"""
    return Template.objects.create(
        name="프리미엄 템플릿",
        description="프리미엄 템플릿입니다",
        thumbnail_url="https://example.com/premium.jpg",
        category="CLASSIC",
        is_premium=True,
        is_active=True,
    )


@pytest.fixture
def inactive_template():
    """비활성화된 템플릿 fixture"""
    return Template.objects.create(
        name="비활성 템플릿",
        description="비활성화된 템플릿입니다",
        thumbnail_url="https://example.com/inactive.jpg",
        category="FLORAL",
        is_premium=False,
        is_active=False,
    )


@pytest.mark.django_db
class TestTemplateList:
    """템플릿 목록 조회 테스트"""

    def test_list_templates(self, api_client, template, premium_template):
        """템플릿 목록 조회 테스트"""
        response = api_client.get("/api/v1/templates/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 2  # 활성화된 템플릿만 조회

    def test_list_templates_excludes_inactive(self, api_client, template, inactive_template):
        """비활성화된 템플릿은 목록에서 제외되는지 테스트"""
        response = api_client.get("/api/v1/templates/")

        assert response.status_code == status.HTTP_200_OK
        template_ids = [t["id"] for t in response.data["results"]]
        assert inactive_template.id not in template_ids

    def test_filter_templates_by_category(self, api_client, template, premium_template):
        """카테고리로 필터링 테스트"""
        # CLASSIC 카테고리 템플릿 추가
        classic_template = Template.objects.create(
            name="클래식 템플릿",
            description="클래식 템플릿",
            thumbnail_url="https://example.com/classic.jpg",
            category="CLASSIC",
            is_premium=False,
            is_active=True,
        )

        response = api_client.get("/api/v1/templates/?category=CLASSIC")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # premium_template과 classic_template
        assert all(t["category"] == "CLASSIC" for t in response.data["results"])

    def test_filter_templates_by_is_premium(self, api_client, template, premium_template):
        """프리미엄 여부로 필터링 테스트"""
        response = api_client.get("/api/v1/templates/?is_premium=true")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["is_premium"] is True
        assert response.data["results"][0]["id"] == premium_template.id

    def test_search_templates_by_name(self, api_client, template, premium_template):
        """이름으로 검색 테스트"""
        response = api_client.get("/api/v1/templates/?search=프리미엄")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert "프리미엄" in response.data["results"][0]["name"]

    def test_search_templates_by_description(self, api_client, template, premium_template):
        """설명으로 검색 테스트"""
        response = api_client.get("/api/v1/templates/?search=테스트용")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == template.id

    def test_order_templates_by_created_at(self, api_client):
        """생성일 기준 정렬 테스트 (기본값: 최신순)"""
        # 오래된 템플릿
        old_template = Template.objects.create(
            name="오래된 템플릿", thumbnail_url="https://example.com/old.jpg", category="MODERN", is_active=True
        )

        # 최신 템플릿
        new_template = Template.objects.create(
            name="최신 템플릿", thumbnail_url="https://example.com/new.jpg", category="MODERN", is_active=True
        )

        response = api_client.get("/api/v1/templates/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == new_template.id  # 최신순
        assert response.data["results"][-1]["id"] == old_template.id

    def test_order_templates_by_usage_count(self, api_client):
        """사용 횟수 기준 정렬 테스트"""
        low_usage = Template.objects.create(
            name="낮은 사용량",
            thumbnail_url="https://example.com/low.jpg",
            category="MODERN",
            usage_count=5,
            is_active=True,
        )

        high_usage = Template.objects.create(
            name="높은 사용량",
            thumbnail_url="https://example.com/high.jpg",
            category="MODERN",
            usage_count=100,
            is_active=True,
        )

        response = api_client.get("/api/v1/templates/?ordering=-usage_count")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == high_usage.id
        assert response.data["results"][0]["usage_count"] == 100


@pytest.mark.django_db
class TestTemplateRetrieve:
    """템플릿 상세 조회 테스트"""

    def test_retrieve_template(self, api_client, template):
        """템플릿 상세 조회 테스트"""
        response = api_client.get(f"/api/v1/templates/{template.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == template.id
        assert response.data["name"] == "테스트 템플릿"
        assert response.data["description"] == "테스트용 템플릿입니다"
        assert response.data["category"] == "MODERN"
        assert response.data["is_premium"] is False
        assert "thumbnail_url" in response.data
        assert "created_at" in response.data

    def test_retrieve_inactive_template(self, api_client, inactive_template):
        """비활성화된 템플릿 조회 시 404 테스트"""
        response = api_client.get(f"/api/v1/templates/{inactive_template.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_template(self, api_client):
        """존재하지 않는 템플릿 조회 시 404 테스트"""
        response = api_client.get("/api/v1/templates/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
