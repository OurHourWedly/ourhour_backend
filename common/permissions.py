"""
커스텀 권한 클래스
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체 소유자만 수정할 수 있는 권한 클래스
    읽기는 모든 인증된 사용자에게 허용
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 인증된 사용자에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한은 객체 소유자에게만 허용
        return obj.user == request.user


class IsInvitationOwner(permissions.BasePermission):
    """
    Invitation 소유자만 접근 가능한 권한
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    공개된 Invitation이거나 소유자인 경우 접근 가능
    """

    def has_object_permission(self, request, view, obj):
        # 소유자는 항상 접근 가능
        if request.user.is_authenticated and obj.user == request.user:
            return True

        # 공개된 Invitation은 인증 없이도 접근 가능
        return obj.is_public and obj.status == "PUBLISHED"
