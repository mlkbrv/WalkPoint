from django.db import models
from django.utils import timezone

from users.models import User


class Partner(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="icons/", null=True, blank=True)

    def __str__(self):
        return self.name


class Reward(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    cost = models.IntegerField(null=True, blank=True)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.partner.name}-{self.description}"


class Step(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()