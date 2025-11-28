from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import BaseUserManager
class CustomUserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser باید is_staff=True باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser باید is_superuser=True باشد.')

        return self.create_user(phone, password, **extra_fields)

class CustomUser(AbstractUser):
    phone_validator = RegexValidator(
        regex=r'^0\d{10}$',
        message='Phone number must start with 0 and be exactly 11 digits.'
    )
    profile_img = models.ImageField(upload_to='img/profile/',null=True,blank=True,default='dp_image.jpg')
    name = models.CharField(max_length=50, blank=True, null=True)
    family = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    code_posti_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='کد پستی باید دقیقاً ۱۰ رقم باشد و فقط شامل عدد باشد.'
)

    username = None
    birth_day = models.DateField(blank=True,null=True)

    objects = CustomUserManager()   # 👈 این مهم‌ترین بخش است!
    class NationalCodeChoices(models.IntegerChoices):
        PERSON = 1, "شخصی"
        COMPANY = 2, "شرکتی"

    national_code = models.IntegerField(
        choices=NationalCodeChoices.choices,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='Phone number'
    )
    code_posti = models.CharField(
        max_length=10,
        unique=True,
        validators=[code_posti_validator],
        verbose_name='code posti',
        null=True,
        blank=True
    )

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True)  
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
