from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class DailyActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    date = models.DateTimeField(default=timezone.now)
    steps = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=timedelta(minutes=0))
    distance_km = models.FloatField(default=0.0)
    calories_burned = models.PositiveIntegerField(default=0)
    source_app = models.CharField(max_length=50, blank=True, null=True,
                                  choices=[('apple_health', 'Apple Health'),
                                           ('google_fit', 'Google Fit'),
                                           ('manual', 'Manual')])

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')
        verbose_name_plural = 'Daily Activities'

    def __str__(self):
        return f"{self.user} - {self.date}: {self.steps} steps"


class CoinTransaction(models.Model):
    class TransactionType(models.TextChoices):
        EARNED = ('EARNED', 'Earned')
        SPENT = ('SPENT', 'Spent')
        ADJUSTMENT = ('ADJUSTMENT', 'Adjustment')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} coins ({self.transaction_type})"
