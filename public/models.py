from django.db import models as m

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
class CustomUser(AbstractUser):
    phone_validator = RegexValidator(
        regex=r'^0\d{10}$',
        message='Phone number must start with 0 and be exactly 11 digits.'
    )
    profile_img = models.ImageField(upload_to='',null=True,blank=True,default='dp_image.jpg')
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

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

class Course(m.Model):
    teacher_id  = m.ForeignKey(CustomUser,on_delete=m.CASCADE,null=True,blank=True)
    title = m.CharField(max_length=255,null=True,blank=True)
    description = m.TextField(null=True,blank=True)
    price = m.IntegerField(null=True,blank=True)
    duration = m.IntegerField (null=True,blank=True)
    duration_type = m.CharField(null=True,blank=True)
    start_date = m.DateField(null=True,blank=True)
    finaly_price = m.IntegerField(null=True,blank=True)
    discount = m.IntegerField(null=True,blank=True)
class Order(m.Model):
    user_id = m.ForeignKey(CustomUser,on_delete=m.CASCADE)
    date = m.DateTimeField(auto_created=True,auto_now_add=True)
    total_price = m.IntegerField()
    class Status(m.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    status = m.CharField(choices=Status)
from django.db import models as m

class Product(m.Model):
    title = m.CharField(max_length=255, null=True, blank=True)
    description = m.TextField(null=True, blank=True)
    price = m.IntegerField(null=True, blank=True)
    finaly_price = m.IntegerField(null=True, blank=True)
    discount = m.IntegerField(null=True, blank=True)
    stock = m.IntegerField()
    # می‌توانی یک تصویر اصلی هم داشته باشی
    main_image = m.ImageField(upload_to='media/product/img', null=True, blank=True)

class ProductImage(m.Model):
    product = m.ForeignKey(Product, on_delete=m.CASCADE, related_name='images')
    image = m.ImageField(upload_to='media/product/img')

    def save(self, *args, **kwargs):
        if self.product.images.count() >= 3 and not self.pk:
            raise ValueError("حداکثر ۳ تصویر می‌توانید اضافه کنید")
        super().save(*args, **kwargs)

class Order_Item(m.Model):
    order_id = m.ForeignKey(Order,on_delete=m.CASCADE)
    product_id = m.ForeignKey(Product,on_delete=m.CASCADE)
    quantity = m.IntegerField()
    price = m.IntegerField()
class Payment(m.Model):
    user_id = m.ForeignKey(CustomUser,on_delete=m.CASCADE)
    order_date = m.DateField(auto_created=True)
    class Status(m.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    status = m.CharField(choices=Status)
    refrence_number = m.CharField()
class Enrollment(m.Model):
    user_id = m.ForeignKey(CustomUser,on_delete=m.CASCADE)
    course_id = m.ForeignKey(Course,on_delete=m.CASCADE)
    enroll_date = m.DateField(auto_created=True)
    class Status(m.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    payment_status = m.CharField(choices=Status)
    
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Banner(m.Model):
    content_type = m.ForeignKey(ContentType, on_delete=m.CASCADE)
    object_id = m.PositiveIntegerField()
    url = GenericForeignKey('content_type', 'object_id')
    img = m.ImageField(upload_to='banners/')
