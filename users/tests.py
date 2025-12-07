from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import tempfile
from PIL import Image

User = get_user_model()


class CustomUserManagerTest(TestCase):
    """Тесты для CustomUserManager"""

    def test_create_user_with_email(self):
        """Тест создания пользователя с email"""
        user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_phone(self):
        """Тест создания пользователя с телефоном"""
        user = User.objects.create_user(
            identifier='+1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.phone_number, '+1234567890')
        self.assertIsNone(user.email)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_requires_identifier(self):
        """Тест что требуется email или телефон"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                identifier='',
                password='testpass123'
            )

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class UserRegistrationTest(TestCase):
    """Тесты для регистрации пользователей"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user_register')

    def test_register_with_email(self):
        """Тест регистрации с email"""
        data = {
            'identifier': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_with_phone(self):
        """Тест регистрации с телефоном"""
        data = {
            'identifier': '+1234567890',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone_number='+1234567890').exists())

    def test_register_password_mismatch(self):
        """Тест что пароли должны совпадать"""
        data = {
            'identifier': 'test@example.com',
            'password': 'testpass123',
            'password2': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Тест что email должен быть уникальным"""
        User.objects.create_user(
            identifier='existing@example.com',
            password='testpass123'
        )
        data = {
            'identifier': 'existing@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_phone(self):
        """Тест что телефон должен быть уникальным"""
        User.objects.create_user(
            identifier='+1234567890',
            password='testpass123'
        )
        data = {
            'identifier': '+1234567890',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTest(TestCase):
    """Тесты для профиля пользователя"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            coins=100
        )
        self.profile_url = reverse('user_profile')
        # Получаем токен для аутентификации
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_profile(self):
        """Тест получения профиля"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['coins'], 100)

    def test_update_profile(self):
        """Тест обновления профиля"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_profile_requires_authentication(self):
        """Тест что профиль требует аутентификации"""
        self.client.credentials()  # Убираем токен
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_readonly_fields(self):
        """Тест что нельзя обновить read-only поля"""
        data = {
            'coins': 9999,
            'email': 'hacked@example.com'
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.coins, 9999)
        self.assertNotEqual(self.user.email, 'hacked@example.com')


class EmailOrPhoneBackendTest(TestCase):
    """Тесты для кастомного бэкенда аутентификации"""

    def setUp(self):
        self.user_email = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123'
        )
        self.user_phone = User.objects.create_user(
            identifier='+1234567890',
            password='testpass123'
        )

    def test_authenticate_with_email(self):
        """Тест аутентификации с email"""
        from users.backends import EmailOrPhoneBackend
        backend = EmailOrPhoneBackend()
        user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user, self.user_email)

    def test_authenticate_with_phone(self):
        """Тест аутентификации с телефоном"""
        from users.backends import EmailOrPhoneBackend
        backend = EmailOrPhoneBackend()
        user = backend.authenticate(
            request=None,
            username='+1234567890',
            password='testpass123'
        )
        self.assertEqual(user, self.user_phone)

    def test_authenticate_wrong_password(self):
        """Тест аутентификации с неправильным паролем"""
        from users.backends import EmailOrPhoneBackend
        backend = EmailOrPhoneBackend()
        user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='wrongpass'
        )
        self.assertIsNone(user)

    def test_authenticate_nonexistent_user(self):
        """Тест аутентификации несуществующего пользователя"""
        from users.backends import EmailOrPhoneBackend
        backend = EmailOrPhoneBackend()
        user = backend.authenticate(
            request=None,
            username='nonexistent@example.com',
            password='testpass123'
        )
        self.assertIsNone(user)
