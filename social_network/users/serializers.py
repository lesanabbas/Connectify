from cryptography.fernet import Fernet
from django.conf import settings
from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import FriendRequest, Activity, Notification
from django.contrib.auth import get_user_model

ENCRYPTION_KEY = settings.ENCRYPTION_KEY
cipher_suite = Fernet(ENCRYPTION_KEY)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False},  
            'last_name': {'required': False}
        }

    def create(self, validated_data):
        encrypted_email = cipher_suite.encrypt(validated_data['email'].lower().encode()).decode()
                
        user = User(
            email=encrypted_email,
            username=validated_data['email'].lower(),
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def to_representation(self, instance):
        
        representation = super().to_representation(instance)
        decrypted_email = cipher_suite.decrypt(instance.email.encode()).decode()
        representation['email'] = decrypted_email
        return representation


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id' ,'from_user', 'to_user', 'created_at', 'is_accepted']
        

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['user', 'action', 'target_user', 'created_at']
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['message', 'is_read', 'created_at']