from rest_framework import serializers
from .models import User, Wishlist, Product, Listing
from django.contrib.auth import authenticate
from datetime import datetime, timedelta

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if User.objects.filter(email=data.get('email')).exists():
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

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Incorrect Credentials")
    
class LinkSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.CharField()
    link = serializers.CharField()
    domain = serializers.CharField()

    def to_representation(self, instance):
        return {
            'title': instance[0],
            'price': instance[1],
            'link': instance[2],
            'domain': instance[3],
        }

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'product', 'store_img_url', 'url', 'title', 'price']

class ProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField()
    listings = ListingSerializer(many=True)
    expires_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'image_url', 'listings', 'expires_at']

    def create(self, validated_data):
        normalised_name = "".join(validated_data['product_name'].split())
        expires_at = datetime.now() + timedelta(hours=24)
        return Product.objects.create(
            normalised_name=normalised_name,
            image_url=validated_data['image_url'],
            expires_at=expires_at
        )
        
    

    

    


