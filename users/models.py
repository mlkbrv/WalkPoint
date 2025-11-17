from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self,identifier,password=None,**extra_fields):
        if '@' in identifier:
            email = self.normalize_email(identifier)
            phone_number = extra_fields.pop('phone_number',None)
        else:
            email = extra_fields.pop('email',None)
            phone_number = identifier

        if not email and not phone_number:
            raise ValueError(_('Users must have an email address or phone number'))

        user = self.model(email=email,phone_number=phone_number,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Staff must have is_staff=True'))

        return self.create_user(email,password,**extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=100,blank=True,null=True)
    last_name = models.CharField(max_length=100,blank=True,null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/",blank=True,null=True)
    email = models.EmailField(_('Email Address'), unique=True, null=True, blank=True)
    phone_number = models.CharField(_('Phone Number'),max_length=20,null=True,blank=True)
    coins = models.IntegerField(default=0)
    overall_steps = models.IntegerField(default=0)
    is_partner = models.BooleanField(default=False, verbose_name="Is Partner Account")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        return self.email or self.phone_number or "User (No identifier)"