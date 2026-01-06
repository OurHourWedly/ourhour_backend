"""
Users 앱 URL 설정
"""

from django.urls import path

from apps.users.views import (
    change_password_view,
    login_view,
    me_view,
    signup_view,
)

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("me/", me_view, name="me"),  # GET: 조회, DELETE: 탈퇴
    path("password/", change_password_view, name="change-password"),
]
