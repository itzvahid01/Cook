from .user_model import CustomUser
from .product_model import Categury
from django.db import models
from django.utils.text import slugify
from public.utils import build_media_path
from django.urls import reverse
from django.utils.functional import cached_property
def course_image_path(instance, filename):
    # مسیر درست برای عکس و ویدئو، title رو هم به kwargs می‌دهیم
    return build_media_path("course", instance=instance, filename=filename, title=instance.title)

class Course(models.Model):
    teacher_id  = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_type = models.ForeignKey(Categury, on_delete=models.CASCADE, null=True, blank=True)
    govahiname = models.BooleanField(default=False)
    class Class_Type(models.TextChoices):
        ONLINE = 'online', "آنلاین"
        IN_PERSON = 'in_person', "حضوری"

    class_type = models.CharField(
        max_length=20,
        choices=Class_Type.choices,
        verbose_name="نوع کلاس",
        null=False,
        blank=False
    )
    
    title = models.CharField(max_length=255, verbose_name="عنوان دوره")
    description = models.TextField(verbose_name="توضیحات دوره")
    
    # فیلدهای جدید اضافه شده
    market_description = models.TextField(
        verbose_name="بازار کار",
        help_text="شرح فرصت‌های شغلی و بازار کار این دوره",
        blank=True,
        null=True
    )
    
    syllabus = models.JSONField(
        verbose_name="سرفصل‌ها",
        default=list,
        help_text="لیست سرفصل‌ها به صورت JSON"
    )
    
    prerequisites = models.JSONField(
        verbose_name="پیش‌نیازها",
        default=list,
        help_text="لیست پیش‌نیازها به صورت JSON"
    )
    
    acquired_skills = models.JSONField(
        verbose_name="مهارت‌های کسب شده",
        default=list,
        help_text="لیست مهارت‌های کسب شده در پایان دوره به صورت JSON"
    )
    
    price = models.IntegerField(default=0, verbose_name="قیمت (تومان)")
    duration = models.IntegerField(verbose_name="مدت دوره (ساعت)")
    
    start_date = models.DateField(verbose_name="تاریخ شروع")
    finaly_price = models.IntegerField(null=True, blank=True, verbose_name="قیمت نهایی")
    discount = models.IntegerField(default=0, blank=True, verbose_name="تخفیف (%)")

    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="اسلاگ")

    image = models.ImageField(
        upload_to=course_image_path,
        default='di_course.png',
        blank=True,
        verbose_name="تصویر دوره"
    )

    video = models.FileField(
        upload_to=course_image_path,
        null=True,
        blank=True,
        verbose_name="ویدئو معرفی"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    update_at  = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
     # ظرفیت کل کلاس
    total_capacity = models.PositiveIntegerField(
        verbose_name='ظرفیت کل کلاس',
        default=30
    )
    
    # تعداد صندلی‌های خالی (این فیلد اصلی است)
    available_seats = models.PositiveIntegerField(
        verbose_name='تعداد صندلی‌های خالی',
        default=30
    )
    def save(self, *args, **kwargs):
        # ساخت slug فقط بار اول
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)
            slug = base
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        # مقداردهی JSON اگر None بود
        if self.syllabus is None:
            self.syllabus = []
        if self.prerequisites is None:
            self.prerequisites = []
        if self.acquired_skills is None:
            self.acquired_skills = []

        # همسان‌سازی available_seats با total_capacity فقط اگر مقدار فعلی بیشتر باشد
        if self.available_seats is None or self.available_seats > self.total_capacity:
            self.available_seats = self.total_capacity

        super().save(*args, **kwargs)

    def enroll_student(self):
        """ثبت‌نام یک دانشجو"""
        if self.available_seats > 0:
            self.available_seats -= 1
            self.save()
            return True
        return False
    
    def unenroll_student(self):
        """لغو ثبت‌نام یک دانشجو"""
        if self.available_seats < self.total_capacity:
            self.available_seats += 1
            self.save()
            return True
        return False
    # متدهای کمکی برای کار با فیلدهای JSON
    def add_syllabus_item(self, title, description="", order=None):
        """اضافه کردن سرفصل جدید"""
        if order is None:
            order = len(self.syllabus) + 1
        
        item = {
            "id": len(self.syllabus) + 1,
            "title": title,
            "description": description,
            "order": order
        }
        
        if not isinstance(self.syllabus, list):
            self.syllabus = []
        
        self.syllabus.append(item)
        self.syllabus = sorted(self.syllabus, key=lambda x: x.get('order', 0))
        return item
    
    def add_prerequisite(self, description, order=None):
        """اضافه کردن پیش‌نیاز جدید"""
        if order is None:
            order = len(self.prerequisites) + 1
        
        item = {
            "id": len(self.prerequisites) + 1,
            "description": description,
            "order": order
        }
        
        if not isinstance(self.prerequisites, list):
            self.prerequisites = []
        
        self.prerequisites.append(item)
        self.prerequisites = sorted(self.prerequisites, key=lambda x: x.get('order', 0))
        return item
    
    def add_acquired_skill(self, description, order=None):
        """اضافه کردن مهارت کسب شده جدید"""
        if order is None:
            order = len(self.acquired_skills) + 1
        
        item = {
            "id": len(self.acquired_skills) + 1,
            "description": description,
            "order": order
        }
        
        if not isinstance(self.acquired_skills, list):
            self.acquired_skills = []
        
        self.acquired_skills.append(item)
        self.acquired_skills = sorted(self.acquired_skills, key=lambda x: x.get('order', 0))
        return item
      
    @property
    def enrolled_count(self):
        """محاسبه ساده"""
        return self.total_capacity - self.available_seats
    
    @property
    def enrollment_stats(self):
        """بدون recursion"""
        enrolled = self.enrolled_count
        return {
            'total_capacity': self.total_capacity,
            'available_seats': self.available_seats,
            'enrolled_count': enrolled,
            'enrollment_percentage': int((enrolled / self.total_capacity) * 100) if self.total_capacity > 0 else 0
        }
    
    @cached_property
    def final_price(self):
        """قیمت نهایی - lazy calculation"""
        if self.discount > 0:
            return self.price * (100 - self.discount) // 100
        return self.price
    
    @cached_property
    def is_full(self):
        """بررسی پر بودن دوره - lazy"""
        return self.available_seats == 0
    
    @cached_property
    def teacher_full_name(self):
        """نام کامل استاد - lazy"""
        if self.teacher_id and self.teacher_id.name and self.teacher_id.family:
            return f"{self.teacher_id.name} {self.teacher_id.family}"
        return getattr(self.teacher_id, 'phone', 'ناشناس') if self.teacher_id else "ناشناس"
    def remove_syllabus_item(self, item_id):
        """حذف سرفصل بر اساس ID"""
        if isinstance(self.syllabus, list):
            self.syllabus = [item for item in self.syllabus if item.get('id') != item_id]
    
    def remove_prerequisite(self, item_id):
        """حذف پیش‌نیاز بر اساس ID"""
        if isinstance(self.prerequisites, list):
            self.prerequisites = [item for item in self.prerequisites if item.get('id') != item_id]
    
    def remove_acquired_skill(self, item_id):
        """حذف مهارت کسب شده بر اساس ID"""
        if isinstance(self.acquired_skills, list):
            self.acquired_skills = [item for item in self.acquired_skills if item.get('id') != item_id]
    
    def get_sorted_syllabus(self):
        """دریافت سرفصل‌های مرتب شده"""
        if isinstance(self.syllabus, list):
            return sorted(self.syllabus, key=lambda x: x.get('order', 0))
        return []
    
    def get_sorted_prerequisites(self):
        """دریافت پیش‌نیازهای مرتب شده"""
        if isinstance(self.prerequisites, list):
            return sorted(self.prerequisites, key=lambda x: x.get('order', 0))
        return []
    
    def get_sorted_acquired_skills(self):
        """دریافت مهارت‌های کسب شده مرتب شده"""
        if isinstance(self.acquired_skills, list):
            return sorted(self.acquired_skills, key=lambda x: x.get('order', 0))
        return []
    
    def get_absolute_url(self):
        """گرفتن URL برای جزئیات دوره"""
        # بستگی به نام URL pattern شما دارد
        return reverse('course-detail', kwargs={'slug': self.slug})
        # یا اگر از id استفاده می‌کنید:
        # return reverse('course-detail', kwargs={'pk': self.pk})
    def __str__(self):
        return self.title or "کورس بدون عنوان"
    
    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        ordering = ['-created_at']
        