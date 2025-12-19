"""
Users 앱 뷰
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.users.serializers import SignupSerializer, LoginSerializer, UserSerializer
from apps.users.services.user_service import UserService


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    회원가입
    
    POST /auth/signup
    """
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = UserService.generate_tokens(user)
        user_data = UserSerializer(user).data
        return Response({
            **user_data,
            'accessToken': tokens['access'],
            'refreshToken': tokens['refresh'],
            'tokenType': 'Bearer'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    로그인
    
    POST /auth/login
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = UserService.authenticate_user(email, password)
        if user:
            tokens = UserService.generate_tokens(user)
            user_data = UserSerializer(user).data
            return Response({
                **user_data,
                'accessToken': tokens['access'],
                'refreshToken': tokens['refresh'],
                'tokenType': 'Bearer'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    현재 사용자 정보 조회
    
    GET /auth/me
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
