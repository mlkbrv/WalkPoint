import uuid
from django.db import models
from users.models import User

class Partner(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    icon = models.ImageField(upload_to="partners_icons/", null=True, blank=True)

    def __str__(self):
        return self.name


class Promotion(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE,related_name='promotions')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    required_steps = models.PositiveIntegerField()
    max_redemptions_per_user = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class UserPromotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redeemed_promotions')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()+self.promotion.title
