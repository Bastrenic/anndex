from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def validate(self, data):
        if (User.objects.filter(email=data.get('email')).exists()):
            raise serializers.ValidationError('Email already exists')
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError('Username already exists')
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
    
    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Incorrect Credentials")
    
