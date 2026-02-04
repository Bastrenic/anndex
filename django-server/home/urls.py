from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView, ProductView, WishlistView, WishlistListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('product', ProductView.as_view(), name='product'),
    path('wishlist', WishlistView.as_view(), name='wishlist-post'),
    path('wishlist/<uuid:wishlist_id>/', WishlistView.as_view(), name='wishlist-detail'),
    path('<str:username>/wishlists', WishlistListView.as_view(), name='wishlist-user')
    
]
