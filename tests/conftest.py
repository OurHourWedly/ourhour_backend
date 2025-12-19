"""
pytest 설정 및 공통 fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """API 클라이언트 fixture"""
    return APIClient()


@pytest.fixture
def user():
    """테스트용 사용자 fixture"""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """인증된 API 클라이언트 fixture"""
    api_client.force_authenticate(user=user)
    return api_client

