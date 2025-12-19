"""
Users 앱 시리얼라이저
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User


class SignupSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': '비밀번호가 일치하지 않습니다.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = User.objects.create_user(
            username=email,  # USERNAME_FIELD가 email이므로 username에 email 값 전달
            email=email,
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """로그인 시리얼라이저"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'provider', 'role', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
