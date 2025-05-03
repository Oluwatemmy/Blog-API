from .models import CustomUser
from django.contrib.auth import authenticate

from rest_framework import serializers

class CustomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False, 'read_only': True},
        }
        read_only_fields = ['id', 'date_joined', 'last_login']

class CustomUserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'password': {'write_only': True, 'min_length': 5, 'max_length': 128}
        }
        read_only_fields = ['id', 'date_joined', 'last_login']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class CustomUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=200,
        required=True,
        style={"input_type": "password", "placeholder": "password"},
    )

