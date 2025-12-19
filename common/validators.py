"""
커스텀 Validators
"""

from django.core.exceptions import ValidationError


def validate_phone_number(value: str) -> None:
    """
    전화번호 형식 검증

    Args:
        value: 검증할 전화번호 문자열

    Raises:
        ValidationError: 전화번호 형식이 올바르지 않은 경우
    """
    import re

    phone_pattern = re.compile(r"^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$")
    if not phone_pattern.match(value):
        raise ValidationError("올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)")
