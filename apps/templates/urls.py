"""
Templates 앱 URL 설정
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.templates.views import TemplateViewSet, UserTemplateViewSet

router = DefaultRouter()
router.register(r"", TemplateViewSet, basename="template")
router.register(r"my", UserTemplateViewSet, basename="user-template")

urlpatterns = router.urls
