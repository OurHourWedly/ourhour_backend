"""
커스텀 예외 클래스 및 예외 핸들러
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class CustomAPIException(Exception):
    """커스텀 API 예외"""

    pass


def custom_exception_handler(exc, context):
    """
    DRF 예외 핸들러 커스터마이징

    Args:
        exc: 예외 객체
        context: 예외가 발생한 컨텍스트

    Returns:
        Response: 커스텀 응답 객체
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "error": {"status_code": response.status_code, "message": str(exc), "detail": response.data}
        }
        response.data = custom_response_data

    return response
