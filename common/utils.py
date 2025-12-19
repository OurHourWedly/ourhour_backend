"""
유틸리티 함수
"""

from typing import Any, Dict
from datetime import datetime


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    datetime 객체를 문자열로 포맷팅

    Args:
        dt: 포맷팅할 datetime 객체
        format_str: 포맷 문자열

    Returns:
        str: 포맷팅된 문자열
    """
    return dt.strftime(format_str)


def get_client_ip(request) -> str:
    """
    요청에서 클라이언트 IP 주소 추출

    Args:
        request: Django request 객체

    Returns:
        str: 클라이언트 IP 주소
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
