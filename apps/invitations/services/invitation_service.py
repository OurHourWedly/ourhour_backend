"""
Invitations 앱 서비스 레이어
비즈니스 로직을 처리하는 레이어
"""
import uuid
from datetime import datetime
from django.utils import timezone
from apps.invitations.models import Invitation


class InvitationService:
    """Invitation 관련 비즈니스 로직 처리"""
    
    @staticmethod
    def generate_unique_slug() -> str:
        """
        고유한 url_slug 생성
        
        Returns:
            str: 고유한 slug 문자열
        """
        max_attempts = 10
        for _ in range(max_attempts):
            slug = uuid.uuid4().hex[:12]
            
            # 중복 체크
            if not Invitation.objects.filter(url_slug=slug).exists():
                return slug
        
        return f"inv-{int(timezone.now().timestamp())}"
    
    @staticmethod
    def publish_invitation(invitation: Invitation) -> Invitation:
        """
        청첩장 발행
        
        Args:
            invitation: Invitation 객체
        
        Returns:
            Invitation: 발행된 Invitation 객체
        
        Raises:
            ValueError: url_slug가 없는 경우
        """
        if not invitation.url_slug:
            invitation.url_slug = InvitationService.generate_unique_slug()
        
        invitation.status = 'PUBLISHED'
        invitation.published_at = timezone.now()
        invitation.save()
        
        return invitation
    
    @staticmethod
    def increment_view_count(invitation: Invitation):
        """
        조회수 증가
        
        Args:
            invitation: Invitation 객체
        """
        invitation.view_count += 1
        invitation.save(update_fields=['view_count'])

