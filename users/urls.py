from django.urls import path
from .views import UserRegisterAPIView,UserProfileAPIView

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('profile/', UserProfileAPIView.as_view(), name='user_profile'),
]
