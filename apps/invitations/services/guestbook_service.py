"""
Guestbook 서비스 레이어
"""
from apps.invitations.models import Guestbook, Invitation


class GuestbookService:
    """Guestbook 관련 비즈니스 로직 처리"""
    
    @staticmethod
    def create_guestbook(invitation: Invitation, author_name: str, message: str, **kwargs) -> Guestbook:
        """
        방명록 생성
        
        Args:
            invitation: Invitation 객체
            author_name: 작성자 이름
            message: 방명록 내용
            **kwargs: 기타 Guestbook 필드들
        
        Returns:
            Guestbook: 생성된 Guestbook 객체
        
        Raises:
            ValueError: enable_guestbook가 False인 경우
        """
        if not invitation.enable_guestbook:
            raise ValueError('이 청첩장은 방명록 기능이 비활성화되어 있습니다.')
        
        guestbook = Guestbook.objects.create(
            invitation=invitation,
            author_name=author_name,
            message=message,
            is_public=kwargs.get('is_public', True),
            phone=kwargs.get('phone', '')
        )
        
        return guestbook

