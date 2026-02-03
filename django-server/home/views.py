import requests
import redis
import logging
from django.shortcuts import render
from django.utils import timezone
from bs4 import BeautifulSoup
from adrf.views import APIView
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ProductSerializer, ListingSerializer
from .models import User, Product
from django.db import connection, IntegrityError
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .scrape_search import search_results
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta
from .helpers import normalise_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAdminUser, AllowAny


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({
            "id": user.id,
            "tokens": {'refresh':str(token), 'access':(str(token.access_token))}
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = RefreshToken.for_user(user)
        return Response({
            "id": user.id,
            "tokens": {'refresh':str(token), 'access':(str(token.access_token))}
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

class ProductView(APIView):
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @method_decorator(cache_page(60 * 60 *  24))
    async def get(self, request):
        query = request.query_params.get('q')
        normalised_name = normalise_string(query)
        
        prod = await sync_to_async(lambda: Product.objects.filter(normalised_name=normalised_name).first())()
        if prod and prod.expires_at >= timezone.now():
            serialized_data = await sync_to_async(lambda: ProductSerializer(prod).data)()
            return Response(serialized_data, status=status.HTTP_200_OK)
        
        listings, image_url = await search_results(query)
        data = {
            'product_name': query,
            'image_url': image_url,
            'listings': listings,
        }
        serializer = await sync_to_async(lambda: ProductSerializer(data=data))()
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        return Response(data, status=status.HTTP_200_OK)

    async def post(self, request):
        prod_data = request.data
        prod_serializer = await sync_to_async(lambda: ProductSerializer(data=prod_data))()
        is_valid = await sync_to_async(lambda: prod_serializer.is_valid())()
        product = await sync_to_async(prod_serializer.save)()

        res = await sync_to_async(lambda: ProductSerializer(product).data)()
        return Response(res, status=status.HTTP_201_CREATED)
        

# get a users wishlist
# create a wishlist
class WishlistView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        #serializer = WishlistSerializer(data=request.data)
        #data = serializer.is_valid(raise_exception=True)
        #wishlist = serializer.save(user=request.user)
        return Response({'message': 'hello'}, status=status.HTTP_200_OK)


    #def get(self, request):
    #    pass
