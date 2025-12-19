"""
공통 시리얼라이저 베이스 클래스
"""

from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    모든 시리얼라이저가 상속받을 기본 시리얼라이저
    공통 필드나 메서드를 정의할 수 있음
    """

    pass
