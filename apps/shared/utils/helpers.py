"""
공통 유틸리티 함수
"""

from typing import Any, Dict, Optional


def get_nested_value(data: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    중첩된 딕셔너리에서 점(.)으로 구분된 키 경로로 값을 가져옴

    Args:
        data: 딕셔너리 데이터
        keys: 점으로 구분된 키 경로 (예: 'user.profile.name')
        default: 기본값

    Returns:
        Any: 찾은 값 또는 기본값
    """
    keys_list = keys.split(".")
    value = data
    for key in keys_list:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
