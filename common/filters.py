"""
필터링 유틸리티
"""
from django_filters import rest_framework as filters


class DateRangeFilter(filters.FilterSet):
    """
    날짜 범위 필터 예시
    """
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')

