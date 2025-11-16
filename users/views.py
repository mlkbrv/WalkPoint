from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer,UserProfileSerializer

User = get_user_model()

class UserRegisterAPIView(generics.CreateAPIView):
    model = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return self.request.user