import re
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models, transaction
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator


def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")


class CustomUserManager(UserManager):
    @transaction.atomic
    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required.")
        if not password:
            raise ValidationError("Password is required.")
        email = self.normalize_email(email)
        validate_password(password)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra.get("is_staff") or not extra.get("is_superuser"):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=255,blank=True, null=True)
    last_name = models.CharField(max_length=255,blank=True, null=True)

    bio = models.TextField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)

    total_steps = models.PositiveIntegerField(default=0)
    available_steps = models.PositiveIntegerField(default=0)

    profile_pic = models.ImageField(
        upload_to="users/profile_pics/",
        null=True, blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    cover = models.ImageField(
        upload_to="users/covers",
        null=True, blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    member_since = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.get_full_name() or self.email

    def transfer_daily_steps(self, date):
        try:
            daily_step = self.daily_steps.get(date=date)
            if daily_step.steps > 0:
                self.total_steps += daily_step.steps
                self.available_steps += daily_step.steps
                self.save(update_fields=['total_steps', 'available_steps'])
                return daily_step.steps
        except DailyStep.DoesNotExist:
            pass
        return 0


class DailyStep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_steps")
    date = models.DateField(default=date.today)
    steps = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")
        ordering = ("-date",)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - {self.date}: {self.steps}"