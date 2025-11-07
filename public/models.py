from django.db import models as m

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models

class CustomUser(AbstractUser):
    # اعتبارسنجی شماره موبایل
    phone_validator = RegexValidator(
        regex=r'^0\d{10}$',
        message='Phone number must start with 0 and be exactly 11 digits.'
    )
    name = models.CharField(max_length=50, verbose_name="name",blank=True,null=True)
    family = models.CharField(max_length=50, verbose_name="family",blank=True,null=True)
    city = models.CharField(max_length=100, verbose_name="city",blank=True,null=True)
    address = models.TextField(verbose_name="address",blank=True,null=True)
    code_posti = models.CharField(max_length=10, verbose_name="code_posti",blank=True,null=True)
    username = None
    # فیلد شماره موبایل (اصلی برای ورود)
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='Phone number'
    )
    # گروه‌ها و دسترسی‌ها (برای جلوگیری از conflict در related_name)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='Groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='User permissions'
    )

    # حالا ورود بر اساس phone انجام میشه
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []  # چون phone برای ورود کافی است

    def __str__(self):
        # اگر username پر بود، نمایش داده میشه، وگرنه phone
        return self.username or self.phone


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
    main_image = m.ImageField(upload_to='product/img', null=True, blank=True)

class ProductImage(m.Model):
    product = m.ForeignKey(Product, on_delete=m.CASCADE, related_name='images')
    image = m.ImageField(upload_to='product/img')

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
