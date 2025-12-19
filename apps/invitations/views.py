"""
Invitations 앱 뷰
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.invitations.models import Invitation
from apps.invitations.serializers import (
    InvitationSerializer,
    InvitationCreateSerializer,
    InvitationUpdateSerializer,
    PublicInvitationSerializer,
    RSVPSerializer,
    RSVPStatisticsSerializer,
    GuestbookSerializer
)
from apps.invitations.services.invitation_service import InvitationService
from apps.invitations.services.rsvp_service import RSVPService
from apps.invitations.services.guestbook_service import GuestbookService
from apps.invitations.models import RSVP, Guestbook
from common.permissions import IsInvitationOwner, IsPublicOrOwner
from rest_framework.pagination import PageNumberPagination


class InvitationViewSet(viewsets.ModelViewSet):
    """
    Invitation ViewSet
    CRUD 및 발행 기능 제공
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """현재 사용자의 청첩장만 조회"""
        return Invitation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvitationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvitationUpdateSerializer
        return InvitationSerializer
    
    def get_permissions(self):
        """retrieve, update, destroy는 소유자만"""
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'publish']:
            return [IsAuthenticated(), IsInvitationOwner()]
        return super().get_permissions()
    
    @action(detail=True, methods=['patch'])
    def publish(self, request, pk=None):
        """
        청첩장 발행
        
        PATCH /invitations/{id}/publish
        """
        invitation = self.get_object()
        invitation = InvitationService.publish_invitation(invitation)
        serializer = self.get_serializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post', 'get'], url_path='rsvps', permission_classes=[AllowAny])
    def rsvps(self, request, pk=None):
        """
        RSVP 생성/조회
        
        POST /invitations/{id}/rsvps/ - RSVP 생성 (인증 불필요, 발행된 청첩장만)
        GET /invitations/{id}/rsvps/ - RSVP 목록 조회 (소유자만)
        """
        invitation = get_object_or_404(
            Invitation,
            pk=pk,
            status='PUBLISHED'
        )
        
        if request.method == 'POST':
            # RSVP 생성 (인증 불필요)
            if not invitation.enable_rsvp:
                return Response(
                    {'error': '이 청첩장은 RSVP 기능이 비활성화되어 있습니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = RSVPSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    # 기존 RSVP가 있는지 확인
                    guest_name = serializer.validated_data['guest_name']
                    phone = serializer.validated_data.get('phone', '')
                    existing_rsvp = RSVP.objects.filter(
                        invitation=invitation,
                        guest_name=guest_name,
                        phone=phone
                    ).first()
                    
                    rsvp = RSVPService.create_or_update_rsvp(
                        invitation=invitation,
                        guest_name=guest_name,
                        guest_count=serializer.validated_data.get('guest_count', 1),
                        attendance_status=serializer.validated_data.get('attendance_status', 'PENDING'),
                        phone=phone,
                        message=serializer.validated_data.get('message', ''),
                        dietary_restrictions=serializer.validated_data.get('dietary_restrictions', '')
                    )
                    response_serializer = RSVPSerializer(rsvp)
                    # 기존 RSVP가 있었으면 200, 없었으면 201
                    return Response(
                        response_serializer.data,
                        status=status.HTTP_200_OK if existing_rsvp else status.HTTP_201_CREATED
                    )
                except ValueError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # GET
            # RSVP 목록 조회 (소유자만)
            if not request.user.is_authenticated or invitation.user != request.user:
                return Response(
                    {'error': '권한이 없습니다.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            rsvps = RSVP.objects.filter(invitation=invitation)
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(rsvps, request)
            
            if page is not None:
                serializer = RSVPSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = RSVPSerializer(rsvps, many=True)
            return Response(serializer.data)
    
    @action(detail=True, methods=['post', 'get'], url_path='guestbooks', permission_classes=[AllowAny])
    def guestbooks(self, request, pk=None):
        """
        방명록 작성/조회
        
        POST /invitations/{id}/guestbooks/ - 방명록 작성 (인증 불필요, 발행된 청첩장만)
        GET /invitations/{id}/guestbooks/ - 방명록 목록 조회 (인증 불필요, 공개만)
        """
        invitation = get_object_or_404(
            Invitation,
            pk=pk,
            status='PUBLISHED'
        )
        
        if request.method == 'POST':
            # 방명록 작성 (인증 불필요)
            if not invitation.enable_guestbook:
                return Response(
                    {'error': '이 청첩장은 방명록 기능이 비활성화되어 있습니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = GuestbookSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    guestbook = GuestbookService.create_guestbook(
                        invitation=invitation,
                        author_name=serializer.validated_data['author_name'],
                        message=serializer.validated_data['message'],
                        phone=serializer.validated_data.get('phone', ''),
                        is_public=serializer.validated_data.get('is_public', True)
                    )
                    response_serializer = GuestbookSerializer(guestbook)
                    return Response(
                        response_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                except ValueError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # GET
            # 방명록 목록 조회 (공개만)
            guestbooks = Guestbook.objects.filter(
                invitation=invitation,
                is_public=True
            )
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(guestbooks, request)
            
            if page is not None:
                serializer = GuestbookSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = GuestbookSerializer(guestbooks, many=True)
            return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='guestbooks/(?P<guestbook_id>[^/.]+)')
    def delete_guestbook(self, request, pk=None, guestbook_id=None):
        """
        방명록 삭제
        
        DELETE /invitations/{id}/guestbooks/{guestbook_id}/ - 방명록 삭제 (소유자만)
        """
        invitation = self.get_object()
        guestbook = get_object_or_404(
            Guestbook,
            pk=guestbook_id,
            invitation=invitation
        )
        
        guestbook.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicInvitationView(APIView):
    """
    공개 청첩장 조회
    
    GET /invitations/slug/{slug}
    인증 불필요
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        invitation = get_object_or_404(
            Invitation,
            url_slug=slug,
            is_public=True,
            status='PUBLISHED'
        )
        
        # 조회수 증가
        InvitationService.increment_view_count(invitation)
        
        serializer = PublicInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicRSVPView(APIView):
    """
    공개 RSVP 통계 조회
    
    GET /invitations/slug/{slug}/rsvps/
    인증 불필요
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        invitation = get_object_or_404(
            Invitation,
            url_slug=slug,
            is_public=True,
            status='PUBLISHED'
        )
        
        statistics = RSVPService.get_rsvp_statistics(invitation)
        serializer = RSVPStatisticsSerializer(statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicGuestbookView(APIView):
    """
    공개 방명록 조회
    
    GET /invitations/slug/{slug}/guestbooks/
    인증 불필요
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        invitation = get_object_or_404(
            Invitation,
            url_slug=slug,
            is_public=True,
            status='PUBLISHED'
        )
        
        guestbooks = Guestbook.objects.filter(
            invitation=invitation,
            is_public=True
        )
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(guestbooks, request)
        
        if page is not None:
            serializer = GuestbookSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = GuestbookSerializer(guestbooks, many=True)
        return Response(serializer.data)

