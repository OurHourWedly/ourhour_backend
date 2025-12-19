"""
Invitation 모델
"""
from django.db import models
from django.conf import settings
from apps.shared.models import BaseModel
from apps.templates.models import Template


class Invitation(BaseModel):
    """
    청첩장 모델
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='소유자'
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations',
        verbose_name='템플릿'
    )
    
    title = models.CharField(max_length=200, verbose_name='청첩장 제목')
    url_slug = models.SlugField(max_length=100, unique=True, verbose_name='URL 슬러그')
    status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=[
            ('DRAFT', '초안'),
            ('PUBLISHED', '발행됨'),
            ('ARCHIVED', '보관됨'),
        ],
        verbose_name='상태'
    )
    
    # 신랑 정보
    groom_name = models.CharField(max_length=50, verbose_name='신랑 이름')
    groom_father_name = models.CharField(max_length=50, blank=True, verbose_name='신랑 아버지')
    groom_mother_name = models.CharField(max_length=50, blank=True, verbose_name='신랑 어머니')
    groom_phone = models.CharField(max_length=20, blank=True, verbose_name='신랑 연락처')
    
    # 신부 정보
    bride_name = models.CharField(max_length=50, verbose_name='신부 이름')
    bride_father_name = models.CharField(max_length=50, blank=True, verbose_name='신부 아버지')
    bride_mother_name = models.CharField(max_length=50, blank=True, verbose_name='신부 어머니')
    bride_phone = models.CharField(max_length=20, blank=True, verbose_name='신부 연락처')
    
    # 예식 정보
    wedding_date = models.DateTimeField(verbose_name='예식 일시')
    wedding_location_name = models.CharField(max_length=200, blank=True, verbose_name='예식장 이름')
    wedding_location_address = models.CharField(max_length=300, blank=True, verbose_name='예식장 주소')
    wedding_location_lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name='위도'
    )
    wedding_location_lng = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name='경도'
    )
    
    # 메시지
    invitation_message = models.TextField(blank=True, verbose_name='본문 메시지')
    greeting_message = models.TextField(blank=True, verbose_name='인사말')
    ending_message = models.TextField(blank=True, verbose_name='엔딩 문구')
    
    # 옵션
    background_animation = models.CharField(max_length=50, blank=True, verbose_name='배경 애니메이션')
    background_color = models.CharField(max_length=20, default='#FFFFFF', verbose_name='배경 색')
    font_family = models.CharField(max_length=50, default='default', verbose_name='폰트')
    music_url = models.URLField(max_length=500, blank=True, verbose_name='배경음악 URL')
    
    # 기능 토글
    enable_rsvp = models.BooleanField(default=True, verbose_name='RSVP 기능 사용')
    enable_guestbook = models.BooleanField(default=True, verbose_name='방명록 기능 사용')
    enable_account_transfer = models.BooleanField(default=False, verbose_name='계좌정보 노출')
    
    # 기타
    is_public = models.BooleanField(default=True, verbose_name='공개 여부')
    view_count = models.IntegerField(default=0, verbose_name='조회수')
    is_paid = models.BooleanField(default=False, verbose_name='결제 여부')
    plan_type = models.CharField(
        max_length=20,
        default='FREE',
        choices=[
            ('FREE', '무료'),
            ('PREMIUM', '프리미엄'),
            ('PREMIUM_PLUS', '프리미엄 플러스'),
        ],
        verbose_name='플랜 타입'
    )
    
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='발행 일시')
    
    class Meta:
        verbose_name = '청첩장'
        verbose_name_plural = '청첩장'
        db_table = 'invitations_invitation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['url_slug']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f'{self.title} ({self.user.email})'


class RSVP(BaseModel):
    """
    RSVP (참석 여부 응답) 모델
    """
    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.CASCADE,
        related_name='rsvps',
        verbose_name='청첩장'
    )
    guest_name = models.CharField(max_length=100, verbose_name='참석자 이름')
    guest_count = models.IntegerField(default=1, verbose_name='참석 인원수')
    attendance_status = models.CharField(
        max_length=20,
        choices=[
            ('ATTENDING', '참석'),
            ('NOT_ATTENDING', '불참석'),
            ('PENDING', '미정'),
        ],
        default='PENDING',
        verbose_name='참석 여부'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='연락처')
    message = models.TextField(blank=True, verbose_name='메시지')
    dietary_restrictions = models.TextField(blank=True, verbose_name='식이 제한사항')
    
    class Meta:
        verbose_name = 'RSVP'
        verbose_name_plural = 'RSVPs'
        db_table = 'invitations_rsvp'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invitation', 'attendance_status']),
        ]
    
    def __str__(self):
        return f'{self.guest_name} - {self.invitation.title} ({self.get_attendance_status_display()})'


class Guestbook(BaseModel):
    """
    방명록 모델
    """
    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.CASCADE,
        related_name='guestbooks',
        verbose_name='청첩장'
    )
    author_name = models.CharField(max_length=100, verbose_name='작성자 이름')
    message = models.TextField(verbose_name='방명록 내용')
    is_public = models.BooleanField(default=True, verbose_name='공개 여부')
    phone = models.CharField(max_length=20, blank=True, verbose_name='연락처')
    
    class Meta:
        verbose_name = '방명록'
        verbose_name_plural = '방명록'
        db_table = 'invitations_guestbook'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invitation', 'is_public']),
        ]
    
    def __str__(self):
        return f'{self.author_name} - {self.invitation.title}'

