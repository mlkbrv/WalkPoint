from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Partner, CouponCategory, CouponTemplate

User = get_user_model()


class PartnerModelTest(TestCase):
    """Тесты для модели Partner"""

    def setUp(self):
        self.user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )

    def test_create_partner(self):
        """Тест создания партнера"""
        partner = Partner.objects.create(
            user=self.user,
            name='Test Partner',
            description='Test Description',
            website='https://test.com'
        )
        self.assertEqual(partner.user, self.user)
        self.assertEqual(partner.name, 'Test Partner')
        self.assertTrue(partner.is_active)

    def test_partner_one_to_one_with_user(self):
        """Тест что партнер связан один-к-одному с пользователем"""
        Partner.objects.create(
            user=self.user,
            name='Test Partner'
        )
        # Попытка создать второго партнера для того же пользователя должна вызвать ошибку
        with self.assertRaises(Exception):
            Partner.objects.create(
                user=self.user,
                name='Another Partner'
            )


class CouponCategoryTest(TestCase):
    """Тесты для CouponCategory"""

    def test_create_category(self):
        """Тест создания категории"""
        category = CouponCategory.objects.create(
            name='Food & Drink',
            slug='food-drink'
        )
        self.assertEqual(category.name, 'Food & Drink')
        self.assertEqual(category.slug, 'food-drink')


class CouponTemplateTest(TestCase):
    """Тесты для CouponTemplate"""

    def setUp(self):
        self.user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=self.user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )

    def test_create_coupon_template(self):
        """Тест создания шаблона купона"""
        template = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='10% Discount',
            description='Get 10% off',
            cost_coins=50,
            validity_days=30
        )
        self.assertEqual(template.partner, self.partner)
        self.assertEqual(template.cost_coins, 50)
        self.assertEqual(template.purchased_count, 0)


class CouponMarketplaceTest(TestCase):
    """Тесты для маркетплейса купонов"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identifier='user@example.com',
            password='testpass123'
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
        self.coupon = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Test Coupon',
            cost_coins=50,
            is_active=True
        )
        # URL для партнеров находятся под /partners/
        self.marketplace_url = '/partners/marketplace/'

    def test_list_active_coupons(self):
        """Тест получения списка активных купонов"""
        response = self.client.get(self.marketplace_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_inactive_coupons_not_listed(self):
        """Тест что неактивные купоны не показываются"""
        inactive_coupon = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Inactive Coupon',
            cost_coins=50,
            is_active=False
        )
        response = self.client.get(self.marketplace_url)
        coupon_titles = [c['title'] for c in response.data]
        self.assertNotIn('Inactive Coupon', coupon_titles)

    def test_marketplace_requires_authentication(self):
        """Тест что маркетплейс требует аутентификации"""
        self.client.credentials()
        response = self.client.get(self.marketplace_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PartnerCouponManagementTest(TestCase):
    """Тесты для управления купонами партнера"""

    def setUp(self):
        self.client = APIClient()
        self.partner_user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=self.partner_user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )
        refresh = RefreshToken.for_user(self.partner_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        # URL для партнеров находятся под /partners/
        self.coupons_url = '/partners/my-coupons/'

    def test_create_coupon(self):
        """Тест создания купона партнером"""
        data = {
            'category': self.category.id,
            'title': 'New Coupon',
            'description': 'Test Description',
            'cost_coins': 100,
            'validity_days': 30
        }
        response = self.client.post(self.coupons_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CouponTemplate.objects.filter(
            partner=self.partner,
            title='New Coupon'
        ).exists())

    def test_list_own_coupons(self):
        """Тест получения списка своих купонов"""
        CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='My Coupon',
            cost_coins=50
        )
        response = self.client.get(self.coupons_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_partner_cannot_create_coupon(self):
        """Тест что не-партнер не может создать купон"""
        regular_user = User.objects.create_user(
            identifier='regular@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'category': self.category.id,
            'title': 'Unauthorized Coupon',
            'cost_coins': 50
        }
        response = self.client.post(self.coupons_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_coupon(self):
        """Тест обновления своего купона"""
        coupon = CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Original Title',
            cost_coins=50
        )
        detail_url = f'/partners/my-coupons/{coupon.id}/'
        data = {
            'category': self.category.id,
            'title': 'Updated Title',
            'cost_coins': 75
        }
        response = self.client.put(detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coupon.refresh_from_db()
        self.assertEqual(coupon.title, 'Updated Title')

    def test_cannot_update_other_partner_coupon(self):
        """Тест что нельзя обновить купон другого партнера"""
        other_partner_user = User.objects.create_user(
            identifier='otherpartner@example.com',
            password='testpass123',
            is_partner=True
        )
        other_partner = Partner.objects.create(
            user=other_partner_user,
            name='Other Partner'
        )
        other_coupon = CouponTemplate.objects.create(
            partner=other_partner,
            category=self.category,
            title='Other Coupon',
            cost_coins=50
        )
        detail_url = f'/partners/my-coupons/{other_coupon.id}/'
        data = {
            'category': self.category.id,
            'title': 'Hacked Title',
            'cost_coins': 50
        }
        response = self.client.put(detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PartnerDashboardTest(TestCase):
    """Тесты для дашборда партнера"""

    def setUp(self):
        self.client = APIClient()
        self.partner_user = User.objects.create_user(
            identifier='partner@example.com',
            password='testpass123',
            is_partner=True
        )
        self.partner = Partner.objects.create(
            user=self.partner_user,
            name='Test Partner'
        )
        self.category = CouponCategory.objects.create(
            name='Food',
            slug='food'
        )
        refresh = RefreshToken.for_user(self.partner_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        # URL для партнеров находятся под /partners/
        self.dashboard_url = '/partners/dashboard/'

    def test_get_dashboard_stats(self):
        """Тест получения статистики дашборда"""
        CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Coupon 1',
            cost_coins=50,
            purchased_count=10
        )
        CouponTemplate.objects.create(
            partner=self.partner,
            category=self.category,
            title='Coupon 2',
            cost_coins=100,
            purchased_count=5
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertEqual(response.data['stats']['total_sold'], 15)
        self.assertEqual(response.data['stats']['revernue_coins'], 1000)  # 10*50 + 5*100
