"""
Users 앱 테스트
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestSignupAPI:
    """회원가입 API 테스트"""
    
    def test_signup_success(self, api_client):
        """회원가입 성공 테스트"""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': '테스트 사용자',
            'phone': '010-1234-5678'
        }
        response = api_client.post('/api/v1/auth/signup/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'accessToken' in response.data
        assert 'refreshToken' in response.data
        assert response.data['email'] == 'newuser@example.com'
        assert response.data['name'] == '테스트 사용자'
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_signup_with_password_mismatch(self, api_client):
        """비밀번호 불일치 테스트"""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'name': '테스트 사용자'
        }
        response = api_client.post('/api/v1/auth/signup/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_signup_with_duplicate_email(self, api_client, user):
        """중복 이메일 테스트"""
        data = {
            'email': 'test@example.com',  # 이미 존재하는 이메일
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': '테스트 사용자'
        }
        response = api_client.post('/api/v1/auth/signup/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_signup_with_weak_password(self, api_client):
        """약한 비밀번호 테스트"""
        data = {
            'email': 'newuser@example.com',
            'password': '123',  # 너무 짧은 비밀번호
            'password_confirm': '123',
            'name': '테스트 사용자'
        }
        response = api_client.post('/api/v1/auth/signup/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    """로그인 API 테스트"""
    
    def test_login_success(self, api_client, user):
        """로그인 성공 테스트"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'accessToken' in response.data
        assert 'refreshToken' in response.data
        assert response.data['email'] == 'test@example.com'
        assert response.data['tokenType'] == 'Bearer'
    
    def test_login_with_wrong_password(self, api_client, user):
        """잘못된 비밀번호 테스트"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_with_nonexistent_email(self, api_client):
        """존재하지 않는 이메일 테스트"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_with_invalid_data(self, api_client):
        """잘못된 데이터 형식 테스트"""
        data = {
            'email': 'invalid-email',  # 이메일 형식 아님
            'password': 'testpass123'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMeAPI:
    """현재 사용자 정보 조회 API 테스트"""
    
    def test_me_success(self, authenticated_client, user):
        """인증된 사용자 정보 조회 성공 테스트"""
        response = authenticated_client.get('/api/v1/auth/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['name'] == user.name
        assert 'id' in response.data
        assert 'date_joined' in response.data
    
    def test_me_unauthorized(self, api_client):
        """인증되지 않은 사용자 접근 테스트"""
        response = api_client.get('/api/v1/auth/me/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
