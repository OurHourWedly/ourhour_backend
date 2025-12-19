"""
재사용 가능한 ViewSet Mixins
"""

from rest_framework import mixins, viewsets


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    생성, 목록 조회, 상세 조회만 허용하는 ViewSet
    """

    pass


class ListRetrieveUpdateViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    목록 조회, 상세 조회, 수정만 허용하는 ViewSet
    """

    pass
