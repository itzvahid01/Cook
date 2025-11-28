from .user_model import CustomUser
from django.db import models
from django.utils.text import slugify
class Course(models.Model):
    teacher_id  = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    price = models.IntegerField(null=True,blank=True)
    duration = models.IntegerField (null=True,blank=True)
    duration_type = models.CharField(null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    finaly_price = models.IntegerField(null=True,blank=True)
    discount = models.IntegerField(null=True,blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title,allow_unicode=True)