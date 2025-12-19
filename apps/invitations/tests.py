"""
Invitations 앱 테스트
"""

from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.invitations.models import RSVP, Guestbook, Invitation
from apps.invitations.services.invitation_service import InvitationService
from apps.templates.models import Template

User = get_user_model()


@pytest.fixture
def template():
    """테스트용 템플릿 fixture"""
    return Template.objects.create(
        name="테스트 템플릿",
        description="테스트용 템플릿",
        thumbnail_url="https://example.com/thumb.jpg",
        category="MODERN",
        is_premium=False,
    )


@pytest.fixture
def invitation(user, template):
    """테스트용 청첩장 fixture"""
    return Invitation.objects.create(
        user=user,
        template=template,
        title="테스트 청첩장",
        url_slug="test-invitation",
        groom_name="홍길동",
        bride_name="김영희",
        wedding_date=timezone.now() + timedelta(days=30),
        status="DRAFT",
    )


@pytest.fixture
def published_invitation(user, template):
    """발행된 청첩장 fixture"""
    return Invitation.objects.create(
        user=user,
        template=template,
        title="발행된 청첩장",
        url_slug="published-invitation",
        groom_name="홍길동",
        bride_name="김영희",
        wedding_date=timezone.now() + timedelta(days=30),
        status="PUBLISHED",
        is_public=True,
        published_at=timezone.now(),
    )


@pytest.fixture
def other_user():
    """다른 사용자 fixture"""
    return User.objects.create_user(
        username="other@example.com",  # USERNAME_FIELD가 email이므로 username에 email 값 전달
        email="other@example.com",
        password="testpass123",
        name="다른 사용자",
    )


@pytest.mark.django_db
class TestInvitationCRUD:
    """청첩장 CRUD 테스트"""

    def test_create_invitation(self, authenticated_client, template):
        """청첩장 생성 테스트"""
        data = {
            "template": template.id,
            "title": "새로운 청첩장",
            "groom_name": "홍길동",
            "bride_name": "김영희",
            "wedding_date": (timezone.now() + timedelta(days=30)).isoformat(),
            "invitation_message": "저희 두 사람이 결혼합니다.",
        }
        response = authenticated_client.post("/api/v1/invitations/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "새로운 청첩장"
        assert response.data["status"] == "DRAFT"
        assert "url_slug" in response.data
        assert Invitation.objects.filter(title="새로운 청첩장").exists()

    def test_list_invitations(self, authenticated_client, user, invitation):
        """청첩장 목록 조회 테스트"""
        # 다른 사용자의 청첩장 생성
        other_user = User.objects.create_user(
            username="other@example.com",  # USERNAME_FIELD가 email이므로 username에 email 값 전달
            email="other@example.com",
            password="testpass123",
            name="다른 사용자",
        )
        Invitation.objects.create(
            user=other_user,
            title="다른 사용자 청첩장",
            url_slug="other-invitation",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
        )

        response = authenticated_client.get("/api/v1/invitations/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1  # 자신의 청첩장만 조회
        assert response.data["results"][0]["title"] == "테스트 청첩장"

    def test_retrieve_invitation(self, authenticated_client, invitation):
        """청첩장 상세 조회 테스트"""
        response = authenticated_client.get(f"/api/v1/invitations/{invitation.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "테스트 청첩장"
        assert response.data["groom_name"] == "홍길동"
        assert response.data["bride_name"] == "김영희"

    def test_update_invitation(self, authenticated_client, invitation):
        """청첩장 수정 테스트"""
        data = {
            "title": "수정된 제목",
            "groom_name": "홍길동",
            "bride_name": "김영희",
            "wedding_date": (timezone.now() + timedelta(days=30)).isoformat(),
        }
        response = authenticated_client.patch(f"/api/v1/invitations/{invitation.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "수정된 제목"
        invitation.refresh_from_db()
        assert invitation.title == "수정된 제목"

    def test_delete_invitation(self, authenticated_client, invitation):
        """청첩장 삭제 테스트"""
        invitation_id = invitation.id
        response = authenticated_client.delete(f"/api/v1/invitations/{invitation_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Invitation.objects.filter(id=invitation_id).exists()

    def test_retrieve_other_user_invitation(self, authenticated_client, other_user, template):
        """다른 사용자의 청첩장 조회 시 404 테스트"""
        other_invitation = Invitation.objects.create(
            user=other_user,
            template=template,
            title="다른 사용자 청첩장",
            url_slug="other-invitation",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
        )

        response = authenticated_client.get(f"/api/v1/invitations/{other_invitation.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_user_invitation(self, authenticated_client, other_user, template):
        """다른 사용자의 청첩장 수정 시 404 테스트"""
        other_invitation = Invitation.objects.create(
            user=other_user,
            template=template,
            title="다른 사용자 청첩장",
            url_slug="other-invitation",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
        )

        data = {"title": "해킹 시도"}
        response = authenticated_client.patch(f"/api/v1/invitations/{other_invitation.id}/", data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestInvitationPublish:
    """청첩장 발행 테스트"""

    def test_publish_invitation(self, authenticated_client, invitation):
        """청첩장 발행 성공 테스트"""
        response = authenticated_client.patch(f"/api/v1/invitations/{invitation.id}/publish/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "PUBLISHED"
        assert "published_at" in response.data
        assert "url_slug" in response.data

        invitation.refresh_from_db()
        assert invitation.status == "PUBLISHED"
        assert invitation.published_at is not None

    def test_publish_invitation_without_slug(self, authenticated_client, user, template):
        """slug가 없는 청첩장 발행 테스트 (자동 생성)"""
        invitation = Invitation.objects.create(
            user=user,
            template=template,
            title="슬러그 없는 청첩장",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
            url_slug="",  # 빈 slug
        )

        response = authenticated_client.patch(f"/api/v1/invitations/{invitation.id}/publish/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "PUBLISHED"
        assert response.data["url_slug"]  # slug가 생성되었는지 확인

        invitation.refresh_from_db()
        assert invitation.url_slug  # slug가 생성되었는지 확인

    def test_publish_other_user_invitation(self, authenticated_client, other_user, template):
        """다른 사용자의 청첩장 발행 시 404 테스트"""
        other_invitation = Invitation.objects.create(
            user=other_user,
            template=template,
            title="다른 사용자 청첩장",
            url_slug="other-invitation",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
        )

        response = authenticated_client.patch(f"/api/v1/invitations/{other_invitation.id}/publish/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPublicInvitationView:
    """공개 청첩장 조회 테스트"""

    def test_get_public_invitation_by_slug(self, api_client, published_invitation):
        """공개 청첩장 slug로 조회 테스트"""
        response = api_client.get(f"/api/v1/invitations/slug/{published_invitation.url_slug}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "발행된 청첩장"
        assert response.data["status"] == "PUBLISHED"
        assert "groom_name" in response.data
        assert "bride_name" in response.data

    def test_get_public_invitation_increments_view_count(self, api_client, published_invitation):
        """공개 청첩장 조회 시 조회수 증가 테스트"""
        initial_count = published_invitation.view_count

        response = api_client.get(f"/api/v1/invitations/slug/{published_invitation.url_slug}/")

        assert response.status_code == status.HTTP_200_OK
        published_invitation.refresh_from_db()
        assert published_invitation.view_count == initial_count + 1

    def test_get_draft_invitation_by_slug(self, api_client, invitation):
        """초안 상태 청첩장 조회 시 404 테스트"""
        invitation.status = "DRAFT"
        invitation.is_public = True
        invitation.save()

        response = api_client.get(f"/api/v1/invitations/slug/{invitation.url_slug}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_private_invitation_by_slug(self, api_client, published_invitation):
        """비공개 청첩장 조회 시 404 테스트"""
        published_invitation.is_public = False
        published_invitation.save()

        response = api_client.get(f"/api/v1/invitations/slug/{published_invitation.url_slug}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_slug(self, api_client):
        """존재하지 않는 slug 조회 시 404 테스트"""
        response = api_client.get("/api/v1/invitations/slug/nonexistent-slug/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestInvitationService:
    """InvitationService 테스트"""

    def test_generate_unique_slug(self):
        """고유한 slug 생성 테스트"""
        slug1 = InvitationService.generate_unique_slug()
        slug2 = InvitationService.generate_unique_slug()

        assert slug1 != slug2
        assert len(slug1) > 0
        assert len(slug2) > 0

    def test_publish_invitation_service(self, invitation):
        """Service를 통한 청첩장 발행 테스트"""
        assert invitation.status == "DRAFT"
        assert invitation.published_at is None

        result = InvitationService.publish_invitation(invitation)

        assert result.status == "PUBLISHED"
        assert result.published_at is not None
        invitation.refresh_from_db()
        assert invitation.status == "PUBLISHED"

    def test_publish_invitation_without_slug(self, user, template):
        """slug가 없는 청첩장 발행 시 자동 생성 테스트"""
        invitation = Invitation.objects.create(
            user=user,
            template=template,
            title="슬러그 없는 청첩장",
            groom_name="홍길동",
            bride_name="김영희",
            wedding_date=timezone.now() + timedelta(days=30),
            url_slug="",
        )

        result = InvitationService.publish_invitation(invitation)

        assert result.url_slug  # slug가 생성되었는지 확인
        assert result.status == "PUBLISHED"

    def test_increment_view_count(self, published_invitation):
        """조회수 증가 테스트"""
        initial_count = published_invitation.view_count

        InvitationService.increment_view_count(published_invitation)

        published_invitation.refresh_from_db()
        assert published_invitation.view_count == initial_count + 1


@pytest.mark.django_db
class TestRSVPAPI:
    """RSVP API 테스트"""

    def test_create_rsvp(self, api_client, published_invitation):
        """RSVP 생성 테스트"""
        data = {
            "guest_name": "김철수",
            "guest_count": 2,
            "attendance_status": "ATTENDING",
            "phone": "010-1234-5678",
            "message": "축하합니다!",
        }
        response = api_client.post(f"/api/v1/invitations/{published_invitation.id}/rsvps/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["guest_name"] == "김철수"
        assert response.data["guest_count"] == 2
        assert response.data["attendance_status"] == "ATTENDING"
        assert RSVP.objects.filter(invitation=published_invitation).exists()

    def test_create_rsvp_when_rsvp_disabled(self, api_client, published_invitation):
        """RSVP 기능이 비활성화된 청첩장에 RSVP 생성 시 실패 테스트"""
        published_invitation.enable_rsvp = False
        published_invitation.save()

        data = {"guest_name": "김철수", "guest_count": 2, "attendance_status": "ATTENDING"}
        response = api_client.post(f"/api/v1/invitations/{published_invitation.id}/rsvps/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_rsvp_on_duplicate(self, api_client, published_invitation):
        """같은 이름/연락처로 중복 RSVP 시 업데이트 테스트"""
        # 첫 번째 RSVP 생성
        RSVP.objects.create(
            invitation=published_invitation,
            guest_name="김철수",
            phone="010-1234-5678",
            attendance_status="PENDING",
            guest_count=1,
        )

        # 같은 이름/연락처로 다시 RSVP
        data = {"guest_name": "김철수", "phone": "010-1234-5678", "attendance_status": "ATTENDING", "guest_count": 2}
        response = api_client.post(f"/api/v1/invitations/{published_invitation.id}/rsvps/", data, format="json")

        assert response.status_code == status.HTTP_200_OK  # 업데이트
        assert response.data["attendance_status"] == "ATTENDING"
        assert response.data["guest_count"] == 2
        assert RSVP.objects.filter(invitation=published_invitation).count() == 1

    def test_list_rsvps_as_owner(self, authenticated_client, published_invitation):
        """소유자가 RSVP 목록 조회 테스트"""
        RSVP.objects.create(
            invitation=published_invitation, guest_name="김철수", attendance_status="ATTENDING", guest_count=2
        )
        RSVP.objects.create(
            invitation=published_invitation, guest_name="이영희", attendance_status="NOT_ATTENDING", guest_count=0
        )

        response = authenticated_client.get(f"/api/v1/invitations/{published_invitation.id}/rsvps/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_rsvps_public_statistics(self, api_client, published_invitation):
        """공개 RSVP 통계 조회 테스트 (slug로 접근)"""
        RSVP.objects.create(
            invitation=published_invitation, guest_name="김철수", attendance_status="ATTENDING", guest_count=2
        )
        RSVP.objects.create(
            invitation=published_invitation, guest_name="이영희", attendance_status="ATTENDING", guest_count=1
        )
        RSVP.objects.create(
            invitation=published_invitation, guest_name="박민수", attendance_status="NOT_ATTENDING", guest_count=0
        )

        response = api_client.get(f"/api/v1/invitations/slug/{published_invitation.url_slug}/rsvps/")

        assert response.status_code == status.HTTP_200_OK
        # 통계 정보만 반환 (개인정보 제외)
        assert "total_count" in response.data or "results" in response.data

    def test_create_rsvp_unauthorized_invitation(self, api_client, invitation):
        """초안 상태 청첩장에 RSVP 생성 시 실패 테스트"""
        data = {"guest_name": "김철수", "attendance_status": "ATTENDING", "guest_count": 1}
        response = api_client.post(f"/api/v1/invitations/{invitation.id}/rsvps/", data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestGuestbookAPI:
    """방명록 API 테스트"""

    def test_create_guestbook(self, api_client, published_invitation):
        """방명록 작성 테스트"""
        data = {"author_name": "김철수", "message": "축하합니다! 행복하세요!", "phone": "010-1234-5678"}
        response = api_client.post(f"/api/v1/invitations/{published_invitation.id}/guestbooks/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["author_name"] == "김철수"
        assert response.data["message"] == "축하합니다! 행복하세요!"
        assert Guestbook.objects.filter(invitation=published_invitation).exists()

    def test_create_guestbook_when_guestbook_disabled(self, api_client, published_invitation):
        """방명록 기능이 비활성화된 청첩장에 방명록 작성 시 실패 테스트"""
        published_invitation.enable_guestbook = False
        published_invitation.save()

        data = {"author_name": "김철수", "message": "축하합니다!"}
        response = api_client.post(f"/api/v1/invitations/{published_invitation.id}/guestbooks/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_guestbooks(self, api_client, published_invitation):
        """방명록 목록 조회 테스트 (인증 불필요)"""
        Guestbook.objects.create(
            invitation=published_invitation, author_name="김철수", message="축하합니다!", is_public=True
        )
        Guestbook.objects.create(
            invitation=published_invitation, author_name="이영희", message="행복하세요!", is_public=True
        )

        response = api_client.get(f"/api/v1/invitations/{published_invitation.id}/guestbooks/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_guestbooks_public_only(self, api_client, published_invitation):
        """공개 방명록만 조회되는지 테스트"""
        Guestbook.objects.create(
            invitation=published_invitation, author_name="김철수", message="공개 메시지", is_public=True
        )
        Guestbook.objects.create(
            invitation=published_invitation, author_name="이영희", message="비공개 메시지", is_public=False
        )

        response = api_client.get(f"/api/v1/invitations/{published_invitation.id}/guestbooks/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["author_name"] == "김철수"

    def test_list_guestbooks_by_slug(self, api_client, published_invitation):
        """slug로 공개 방명록 조회 테스트"""
        Guestbook.objects.create(
            invitation=published_invitation, author_name="김철수", message="축하합니다!", is_public=True
        )

        response = api_client.get(f"/api/v1/invitations/slug/{published_invitation.url_slug}/guestbooks/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_delete_guestbook_as_owner(self, authenticated_client, published_invitation):
        """소유자가 방명록 삭제 테스트"""
        guestbook = Guestbook.objects.create(
            invitation=published_invitation, author_name="김철수", message="삭제될 메시지", is_public=True
        )

        response = authenticated_client.delete(
            f"/api/v1/invitations/{published_invitation.id}/guestbooks/{guestbook.id}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Guestbook.objects.filter(id=guestbook.id).exists()

    def test_delete_guestbook_unauthorized(self, api_client, published_invitation):
        """인증되지 않은 사용자가 방명록 삭제 시 실패 테스트"""
        guestbook = Guestbook.objects.create(
            invitation=published_invitation, author_name="김철수", message="삭제되지 않을 메시지", is_public=True
        )

        response = api_client.delete(f"/api/v1/invitations/{published_invitation.id}/guestbooks/{guestbook.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_guestbook_unauthorized_invitation(self, api_client, invitation):
        """초안 상태 청첩장에 방명록 작성 시 실패 테스트"""
        data = {"author_name": "김철수", "message": "축하합니다!"}
        response = api_client.post(f"/api/v1/invitations/{invitation.id}/guestbooks/", data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
