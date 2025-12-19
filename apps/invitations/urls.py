"""
Invitations 앱 URL 설정
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.invitations.views import (
    InvitationViewSet,
    PublicGuestbookView,
    PublicInvitationView,
    PublicRSVPView,
)

router = DefaultRouter()
router.register(r"", InvitationViewSet, basename="invitation")

urlpatterns = [
    path("slug/<str:slug>/", PublicInvitationView.as_view(), name="public-invitation"),
    path("slug/<str:slug>/rsvps/", PublicRSVPView.as_view(), name="public-rsvp-statistics"),
    path("slug/<str:slug>/guestbooks/", PublicGuestbookView.as_view(), name="public-guestbooks"),
] + router.urls
