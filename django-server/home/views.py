import requests
from django.shortcuts import render
#from rest_framework.views import APIView
from adrf.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, SearchSerializer, ProductSerializer, ListingSerializer
from .models import User
from django.db import connection, IntegrityError
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from bs4 import BeautifulSoup
from .scrape_search import search_results


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
    async def get(self, request):
        query = request.query_params.get('q')
        res = await search_results(query)
        serializer = ProductSerializer(res, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        prod_data = {
            'product_name': data['product_name'],
            'image_url': data['image_url'],
        }
        prod_serializer = ProductSerializer(data=prod_data)
        prod_serializer.is_valid(raise_exception=True)
        prod_serializer.save()

        listings = data['listings']
        for l in listings:
            list_serializer = ListingSerializer(data=l)
            list_serializer.is_valid(raise_exception=True)
            list_serializer.save(product=prod_serializer.instance)
        return Response({'message': 'saved'}, status=status.HTTP_200_OK)


# get a users wishlist
# create a wishlist
class WishlistView(APIView):
    def post(self, request):
        print(request)
        if not request.user.is_authenticated:
            return Response({'message': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        print(request.user)
        #serializer = WishlistSerializer(data=request.data)
        #data = serializer.is_valid(raise_exception=True)
        #wishlist = serializer.save(user=request.user)
        return Response({'message': 'hello'}, status=status.HTTP_200_OK)


    #def get(self, request):
    #    pass

"""
{

    "username": "ajl",
    "email": "ajl@penis.com",
    "password": "ajl"
}

[
    {
        "title": "PS5 PlayStation 5 Pro Console",
        "price": "1199",
        "link": "https://www.jbhifi.com.au/pages/playstation-5/",
        "domain": "jbhifi.com.au"
    },
    {
        "title": "Disc Drive For PS5 Digital Edition or Pro Console",
        "price": "124",
        "link": "https://www.bigw.com.au/gaming/ps5/ps5-consoles/c/64121178100/",
        "domain": "bigw.com.au"
    },
    {
        "title": "PlayStation 5 Console Slim",
        "price": "829",
        "link": "https://www.thegoodguys.com.au/gaming/gaming-hardware/playstation-consoles/",
        "domain": "thegoodguys.com.au"
    },
    {
        "title": "PS5 PlayStation 5 Pro Console",
        "price": "1198",
        "link": "https://www.harveynorman.com.au/games-hub/game-consoles/playstation-consoles/",
        "domain": "harveynorman.com.au"
    },
    {
        "title": "PlayStation 5 Pro Console",
        "price": "1,199.95",
        "link": "https://store.sony.com.au/playstation-5-console/",
        "domain": "store.sony.com.au"
    }
]
"""