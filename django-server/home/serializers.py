from rest_framework import serializers
from .models import User, Wishlist, Product, Listing
from django.contrib.auth import authenticate
from datetime import timedelta
from django.utils import timezone
from .helpers import normalise_string

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
    
class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'domain', 'link', 'name', 'price']

class ProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='normalised_name')
    listings = ListingSerializer(many=True)
    expires_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'image_url', 'listings', 'expires_at']

    def create(self, validated_data):
        normalised_name = normalise_string(validated_data['normalised_name'])
        expires_at = timezone.now() + timedelta(hours=24)
        prod = Product.objects.create(
            normalised_name=normalised_name,
            image_url=validated_data['image_url'],
            expires_at=expires_at
        )

        for listing in validated_data['listings']:
            Listing.objects.create(product=prod, **listing)
        return prod

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Product.objects.all(),
        write_only = True,
        source='products'
    )
    class Meta:
        model = Wishlist
        fields = ['id', 'title', 'products', 'product_ids']
        
    

    

    


