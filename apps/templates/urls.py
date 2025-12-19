"""
Templates 앱 URL 설정
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.templates.views import TemplateViewSet

router = DefaultRouter()
router.register(r'', TemplateViewSet, basename='template')

urlpatterns = router.urls

