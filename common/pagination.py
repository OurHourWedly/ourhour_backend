"""
DRF 커스텀 페이지네이션
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    표준 페이지네이션 클래스

    Attributes:
        page_size: 기본 페이지 크기
        page_size_query_param: 페이지 크기를 지정할 수 있는 쿼리 파라미터
        max_page_size: 최대 페이지 크기
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
