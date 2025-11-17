from django.db import models
from django.conf import settings

class CouponCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Coupon Categories"

    def __str__(self):
        return self.name

class Partner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='partner')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='partners_logo/', blank=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CouponTemplate(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='coupons')
    category = models.ForeignKey(CouponCategory, on_delete=models.CASCADE, related_name='coupons')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    cost_coins = models.PositiveIntegerField()
    validity_days = models.PositiveIntegerField(default=30)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    purchased_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.partner.name}"

