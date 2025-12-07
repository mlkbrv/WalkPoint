from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from partners.models import Partner, CouponCategory, CouponTemplate
from .models import UserCoupon
import uuid

User = get_user_model()


class BuyCouponTest(TestCase):
    """Тесты для покупки купонов"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='user@example.com',
            password='testpass123',
            coins=200
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Создаем партнера и купон
        partner_user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=partner_user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )
        self.coupon_template = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Test Coupon',
            cost_coins=100,
            is_active=True
        )

    def test_buy_coupon_success(self):
        """Тест успешной покупки купона"""
        buy_url = reverse('buy_coupon', kwargs={'template_id': self.coupon_template.id})
        response = self.client.post(buy_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем что монеты списались
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 100)  # Было 200, стало 100
        
        # Проверяем что купон создан
        self.assertTrue(UserCoupon.objects.filter(
            user=self.user,
            template=self.coupon_template
        ).exists())
        
        # Проверяем что счетчик покупок увеличился
        self.coupon_template.refresh_from_db()
        self.assertEqual(self.coupon_template.purchased_count, 1)

    def test_buy_coupon_insufficient_coins(self):
        """Тест покупки при недостатке монет"""
        self.user.coins = 50
        self.user.save()
        
        buy_url = reverse('buy_coupon', kwargs={'template_id': self.coupon_template.id})
        response = self.client.post(buy_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Недостаточно', response.data['error'])

    def test_buy_inactive_coupon(self):
        """Тест покупки неактивного купона"""
        self.coupon_template.is_active = False
        self.coupon_template.save()
        
        buy_url = reverse('buy_coupon', kwargs={'template_id': self.coupon_template.id})
        response = self.client.post(buy_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_coupon_with_limited_quantity(self):
        """Тест покупки купона с ограниченным количеством"""
        self.coupon_template.quantity = 1
        self.coupon_template.save()
        
        # Первая покупка должна пройти
        buy_url = reverse('buy_coupon', kwargs={'template_id': self.coupon_template.id})
        response = self.client.post(buy_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Вторая покупка должна провалиться
        other_user = User.objects.create_user(
            identifier='other@example.com',
            password='testpass123',
            coins=200
        )
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(buy_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('закончились', response.data['error'])

    def test_buy_coupon_creates_qr_code(self):
        """Тест что при покупке создается QR код"""
        buy_url = reverse('buy_coupon', kwargs={'template_id': self.coupon_template.id})
        response = self.client.post(buy_url)
        user_coupon = UserCoupon.objects.get(user=self.user)
        self.assertIsNotNone(user_coupon.qr_code_image)
        self.assertIsNotNone(user_coupon.redemption_uuid)


class MyCouponsTest(TestCase):
    """Тесты для списка купонов пользователя"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='user@example.com',
            password='testpass123',
            coins=500
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Создаем партнера и купоны
        partner_user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=partner_user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )
        self.coupon_template = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Test Coupon',
            cost_coins=100,
            is_active=True
        )
        self.my_coupons_url = reverse('my_coupons')

    def test_list_my_coupons(self):
        """Тест получения списка своих купонов"""
        UserCoupon.objects.create(
            user=self.user,
            template=self.coupon_template
        )
        UserCoupon.objects.create(
            user=self.user,
            template=self.coupon_template,
            is_redeemed=True
        )
        
        response = self.client.get(self.my_coupons_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Неиспользованные должны быть первыми
        self.assertFalse(response.data[0]['is_redeemed'])

    def test_my_coupons_requires_authentication(self):
        """Тест что требуется аутентификация"""
        self.client.credentials()
        response = self.client.get(self.my_coupons_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_coupons(self):
        """Тест что пользователь видит только свои купоны"""
        other_user = User.objects.create_user(
            identifier='other@example.com',
            password='testpass123'
        )
        UserCoupon.objects.create(
            user=self.user,
            template=self.coupon_template
        )
        UserCoupon.objects.create(
            user=other_user,
            template=self.coupon_template
        )
        
        response = self.client.get(self.my_coupons_url)
        self.assertEqual(len(response.data), 1)


class RedeemCouponTest(TestCase):
    """Тесты для погашения купонов"""

    def setUp(self):
        self.client = APIClient()
        
        # Создаем пользователя и купон
        self.user = User.objects.create_user(
            identifier='user@example.com',
            password='testpass123',
            coins=200
        )
        partner_user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=partner_user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )
        self.coupon_template = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Test Coupon',
            cost_coins=100
        )
        self.user_coupon = UserCoupon.objects.create(
            user=self.user,
            template=self.coupon_template,
            redemption_uuid=uuid.uuid4()
        )

    def test_redeem_coupon_success(self):
        """Тест успешного погашения купона"""
        refresh = RefreshToken.for_user(self.partner.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        redeem_url = reverse('redeem_coupon', kwargs={'uuid': self.user_coupon.redemption_uuid})
        response = self.client.post(redeem_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user_coupon.refresh_from_db()
        self.assertTrue(self.user_coupon.is_redeemed)
        self.assertIsNotNone(self.user_coupon.redeemed_at)

    def test_redeem_already_redeemed_coupon(self):
        """Тест погашения уже использованного купона"""
        self.user_coupon.is_redeemed = True
        self.user_coupon.redeemed_at = timezone.now()
        self.user_coupon.save()
        
        refresh = RefreshToken.for_user(self.partner.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        redeem_url = reverse('redeem_coupon', kwargs={'uuid': self.user_coupon.redemption_uuid})
        response = self.client.post(redeem_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('уже использован', response.data['error'])

    def test_redeem_requires_partner_permission(self):
        """Тест что погашение требует прав партнера"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        redeem_url = reverse('redeem_coupon', kwargs={'uuid': self.user_coupon.redemption_uuid})
        response = self.client.post(redeem_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_redeem_other_partner_coupon(self):
        """Тест что нельзя погасить купон другого партнера"""
        other_partner_user = User.objects.create_user(
            identifier='otherpartner@example.com',
            password='testpass123',
            is_partner=True
        )
        other_partner = Partner.objects.create(
            user=other_partner_user,
            name='Other Partner'
        )
        
        refresh = RefreshToken.for_user(other_partner_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        redeem_url = reverse('redeem_coupon', kwargs={'uuid': self.user_coupon.redemption_uuid})
        response = self.client.post(redeem_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
