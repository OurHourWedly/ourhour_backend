"""
Users 앱 서비스 레이어
비즈니스 로직을 처리하는 레이어
"""

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User


class UserService:
    """User 관련 비즈니스 로직 처리"""

    @staticmethod
    def create_user(email: str, password: str, name: str, phone: str = None):
        """
        사용자 생성

        Args:
            email: 이메일
            password: 비밀번호
            name: 이름
            phone: 전화번호 (선택)

        Returns:
            User: 생성된 사용자 객체
        """
        user = User.objects.create_user(
            username=email,  # USERNAME_FIELD가 email이므로 username에 email 값 전달
            email=email,
            password=password,
            name=name,
            phone=phone or "",
        )
        return user

    @staticmethod
    def authenticate_user(email: str, password: str):
        """
        사용자 인증

        Args:
            email: 이메일
            password: 비밀번호

        Returns:
            User: 인증된 사용자 객체 또는 None
        """
        return authenticate(email=email, password=password)

    @staticmethod
    def generate_tokens(user: User):
        """
        JWT 토큰 생성

        Args:
            user: User 객체

        Returns:
            dict: access_token, refresh_token
        """
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
