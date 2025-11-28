from django.utils.text import slugify
from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
class Banner(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    url = GenericForeignKey('content_type', 'object_id')
    img = models.ImageField(upload_to='banners/')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title,allow_unicode=True)
        super().save(*args, **kwargs)