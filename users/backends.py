# accounts/backends.py (Обновленная версия)
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

UserModel = get_user_model()


class EmailOrPhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None

        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(phone_number=username)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None