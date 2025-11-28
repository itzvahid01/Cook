from django.core.exceptions import ValidationError
from PIL import Image
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
class Categury(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    cat_img = models.ImageField(upload_to='img/categury', default='di_categury.jpg')
    
    # اضافه کردن مقادیر ثابت برای ابعاد
    REQUIRED_WIDTH = 250
    REQUIRED_HEIGHT = 125
    TOLERANCE = 200
    def get_absolute_url(self):
        return reverse('categury-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # ساخت slug اگر وجود ندارد
        if not self.slug and self.title:
            self.slug = slugify(self.title, allow_unicode=True)
            counter = 1
            original_slug = self.slug
            while Categury.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)  # ذخیره اولیه برای دسترسی به فایل image

        # بررسی و اصلاح ابعاد cat_img
        if self.cat_img:
            img = Image.open(self.cat_img.path)
            width, height = img.size

            # اگر ابعاد خیلی متفاوت بود، ارور بده
            if abs(width - self.REQUIRED_WIDTH) > self.TOLERANCE or abs(height - self.REQUIRED_HEIGHT) > self.TOLERANCE:
                raise ValidationError(
                    f"ابعاد تصویر اصلی باید نزدیک {self.REQUIRED_WIDTH}x{self.REQUIRED_HEIGHT} باشد "
                    f"(اندازه فعلی: {width}x{height})"
                )

            # اگر نزدیک بود، resize کن دقیقاً روی ابعاد مورد نظر
            if width != self.REQUIRED_WIDTH or height != self.REQUIRED_HEIGHT:
                img = img.resize((self.REQUIRED_WIDTH, self.REQUIRED_HEIGHT), Image.LANCZOS)
                img.save(self.cat_img.path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField(max_length=255)
    cat = models.ForeignKey(Categury,models.CASCADE)
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.IntegerField()
    discount = models.IntegerField()
    tag = models.ForeignKey(Tag,models.CASCADE)
    stock = models.IntegerField()
    weight = models.IntegerField()
    expiration_date = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 
    product_img = models.ImageField(
        upload_to='img/product/', 
        null=True, 
        blank=True, 
        default='di_cook.png'
    )

    REQUIRED_WIDTH = 600
    REQUIRED_HEIGHT = 400
    TOLERANCE = 100  # اختلاف مجاز
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})
    def save(self, *args, **kwargs):
        # ساخت slug اگر وجود ندارد
        if not self.slug and self.title:
            self.slug = slugify(self.title, allow_unicode=True)
            counter = 1
            original_slug = self.slug
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)  # ذخیره اولیه برای دسترسی به فایل image

        # بررسی و اصلاح ابعاد product_img
        if self.product_img:
            img = Image.open(self.product_img.path)
            width, height = img.size

            if abs(width - self.REQUIRED_WIDTH) > self.TOLERANCE or abs(height - self.REQUIRED_HEIGHT) > self.TOLERANCE:
                raise ValidationError(
                    f"ابعاد تصویر اصلی باید نزدیک {self.REQUIRED_WIDTH}x{self.REQUIRED_HEIGHT} باشد "
                    f"(اندازه فعلی: {width}x{height})"
                )

            if width != self.REQUIRED_WIDTH or height != self.REQUIRED_HEIGHT:
                img = img.resize((self.REQUIRED_WIDTH, self.REQUIRED_HEIGHT), Image.LANCZOS)
                img.save(self.product_img.path)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/img')
    created_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True) 

    REQUIRED_WIDTH = 600
    REQUIRED_HEIGHT = 400
    TOLERANCE = 100

    def save(self, *args, **kwargs):
        if self.product.images.count() >= 3 and not self.pk:
            raise ValidationError("حداکثر ۳ تصویر می‌توانید اضافه کنید")
        
        super().save(*args, **kwargs)  # ذخیره اولیه برای دسترسی به فایل image

        img = Image.open(self.image.path)
        width, height = img.size

        # اگر اندازه خیلی متفاوت بود، ارور بده
        if abs(width - self.REQUIRED_WIDTH) > self.TOLERANCE or abs(height - self.REQUIRED_HEIGHT) > self.TOLERANCE:
            # می‌تونی خودت resize کنی یا ارور بده
            raise ValidationError(
                f"ابعاد تصویر باید نزدیک {self.REQUIRED_WIDTH}x{self.REQUIRED_HEIGHT} باشد. "
                f"(اندازه فعلی: {width}x{height})"
            )

        # اگر نزدیک بود، خودش resize کنه دقیقاً روی 600x400
        if width != self.REQUIRED_WIDTH or height != self.REQUIRED_HEIGHT:
            img = img.resize((self.REQUIRED_WIDTH, self.REQUIRED_HEIGHT), Image.LANCZOS)
            img.save(self.image.path)
