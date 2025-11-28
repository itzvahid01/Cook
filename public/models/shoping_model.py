from django.db import models
from .user_model import CustomUser
from django.utils.text import slugify
from .product_model import Product
from .course_model import Course
class Order(models.Model):
    user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField()
    class Status(models.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    status = models.CharField(choices=Status)
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
class Order_Item(models.Model):
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 
class Payment(models.Model):
    user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    order_date = models.DateField(auto_created=True)
    class Status(models.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    status = models.CharField(choices=Status)
    refrence_number = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 
class Enrollment(models.Model):
    user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course,on_delete=models.CASCADE)
    enroll_date = models.DateField(auto_created=True)
    class Status(models.TextChoices):
        waiting = 'در انتظار پرداخت'
        done = 'پرداخت شده'
    payment_status = models.CharField(choices=Status)
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 