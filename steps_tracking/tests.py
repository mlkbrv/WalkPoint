from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from .models import DailyActivity, CoinTransaction

User = get_user_model()


class DailyActivityTest(TestCase):
    """Тесты для DailyActivity"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            coins=0
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.activity_url = reverse('daily_activity_list_create')

    def test_create_activity(self):
        """Тест создания активности"""
        # Используем текущую дату и время
        now = timezone.now()
        data = {
            'date': now.isoformat(),
            'steps': 10000,
            'duration': 3600,
            'distance_km': 7.5,
            'calories_burned': 300,
            'source_app': 'manual'
        }
        response = self.client.post(self.activity_url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DailyActivity.objects.filter(user=self.user).exists())

    def test_list_activities(self):
        """Тест получения списка активностей"""
        DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=5000
        )
        DailyActivity.objects.create(
            user=self.user,
            date=timezone.now() - timedelta(days=1),
            steps=8000
        )
        response = self.client.get(self.activity_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_activity_unique_per_day(self):
        """Тест что может быть только одна активность на день"""
        date = timezone.now()
        DailyActivity.objects.create(
            user=self.user,
            date=date,
            steps=5000
        )
        data = {
            'date': date.isoformat(),
            'steps': 6000
        }
        response = self.client.post(self.activity_url, data, format='json')
        # Должно вернуть ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activity_requires_authentication(self):
        """Тест что требуется аутентификация"""
        self.client.credentials()
        data = {
            'date': timezone.now().isoformat(),
            'steps': 5000
        }
        response = self.client.post(self.activity_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_activity_auto_assigns_user(self):
        """Тест что активность автоматически привязывается к пользователю"""
        now = timezone.now()
        data = {
            'date': now.isoformat(),
            'steps': 5000
        }
        response = self.client.post(self.activity_url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        activity = DailyActivity.objects.get(user=self.user)
        self.assertEqual(activity.user, self.user)


class CoinTransactionTest(TestCase):
    """Тесты для CoinTransaction"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            coins=0
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.transactions_url = reverse('coin_transaction_list')

    def test_list_transactions(self):
        """Тест получения списка транзакций"""
        CoinTransaction.objects.create(
            user=self.user,
            amount=10,
            transaction_type=CoinTransaction.TransactionType.EARNED,
            reason='Test reward'
        )
        CoinTransaction.objects.create(
            user=self.user,
            amount=5,
            transaction_type=CoinTransaction.TransactionType.SPENT,
            reason='Test purchase'
        )
        response = self.client.get(self.transactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_transactions_require_authentication(self):
        """Тест что требуется аутентификация"""
        self.client.credentials()
        response = self.client.get(self.transactions_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_transactions(self):
        """Тест что пользователь видит только свои транзакции"""
        other_user = User.objects.create_user(
            identifier='other@example.com',
            password='testpass123'
        )
        CoinTransaction.objects.create(
            user=self.user,
            amount=10,
            transaction_type=CoinTransaction.TransactionType.EARNED,
            reason='My transaction'
        )
        CoinTransaction.objects.create(
            user=other_user,
            amount=20,
            transaction_type=CoinTransaction.TransactionType.EARNED,
            reason='Other transaction'
        )
        response = self.client.get(self.transactions_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason'], 'My transaction')


class DailyRewardSignalTest(TestCase):
    """Тесты для сигнала начисления монет за шаги"""

    def setUp(self):
        self.user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            coins=0
        )

    def test_reward_for_5000_steps(self):
        """Тест начисления за 5000 шагов (5 монет)"""
        activity = DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=5000
        )
        self.user.refresh_from_db()
        # 5000 шагов = 5 монет (1 за каждые 1000)
        self.assertEqual(self.user.coins, 5)
        self.assertTrue(CoinTransaction.objects.filter(
            user=self.user,
            transaction_type=CoinTransaction.TransactionType.EARNED
        ).exists())

    def test_reward_for_10000_steps(self):
        """Тест начисления за 10000 шагов (10 монет)"""
        activity = DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=10000
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 10)

    def test_no_reward_below_threshold(self):
        """Тест что нет награды за шаги меньше 5000"""
        activity = DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=4000
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 0)
        self.assertFalse(CoinTransaction.objects.filter(
            user=self.user,
            transaction_type=CoinTransaction.TransactionType.EARNED
        ).exists())

    def test_reward_update_on_activity_update(self):
        """Тест обновления награды при обновлении активности"""
        activity = DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=5000
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 5)
        
        # Обновляем количество шагов
        activity.steps = 8000
        activity.save()
        self.user.refresh_from_db()
        # Должно быть 8 монет (разница 3 монеты)
        self.assertEqual(self.user.coins, 8)
        
        # Проверяем что транзакция обновлена, а не создана новая
        transactions = CoinTransaction.objects.filter(
            user=self.user,
            transaction_type=CoinTransaction.TransactionType.EARNED
        )
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first().amount, 8)

    def test_reward_removed_when_steps_below_threshold(self):
        """Тест удаления награды когда шаги падают ниже порога"""
        activity = DailyActivity.objects.create(
            user=self.user,
            date=timezone.now(),
            steps=6000
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 6)
        
        # Уменьшаем шаги ниже порога
        activity.steps = 4000
        activity.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 0)
        self.assertFalse(CoinTransaction.objects.filter(
            user=self.user,
            transaction_type=CoinTransaction.TransactionType.EARNED
        ).exists())
