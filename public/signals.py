import os
import shutil
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Categury, Product, ProductImage, Course, CustomUser

# -----------------------------
# توابع کمکی
# -----------------------------
def remove_file(file_field, default_name=None):
    """حذف فایل اگر وجود داشته باشد و نامش برابر default_name نباشد"""
    if file_field and file_field.name != default_name:
        if os.path.isfile(file_field.path):
            os.remove(file_field.path)

def remove_folder_if_empty(file_field):
    """حذف فولدر حاوی فایل اگر خالی باشد"""
    if file_field:
        folder = os.path.dirname(file_field.path)
        if os.path.isdir(folder) and not os.listdir(folder):
            shutil.rmtree(folder)

# -----------------------------
# سیگنال pre_delete
# -----------------------------
@receiver(pre_delete, sender=Categury)
def delete_categury_files(sender, instance, **kwargs):
    remove_file(instance.cat_img, 'di_categury.jpg')
    remove_folder_if_empty(instance.cat_img)

@receiver(pre_delete, sender=Product)
def delete_product_files(sender, instance, **kwargs):
    remove_file(instance.product_img, 'di_cook.png')
    remove_folder_if_empty(instance.product_img)

@receiver(pre_delete, sender=ProductImage)
def delete_productimage_file(sender, instance, **kwargs):
    remove_file(instance.image)
    remove_folder_if_empty(instance.image)

@receiver(pre_delete, sender=Course)
def delete_course_files(sender, instance, **kwargs):
    remove_file(instance.image, 'di_course.png')
    remove_folder_if_empty(instance.image)
    # در صورت نیاز می‌توان ویدئو را هم پاک کرد
    remove_file(instance.video)
    remove_folder_if_empty(instance.video)

@receiver(pre_delete, sender=CustomUser)
def delete_profile_image(sender, instance, **kwargs):
    remove_file(instance.profile_img, 'dp_image.jpg')
    remove_folder_if_empty(instance.profile_img)

# -----------------------------
# سیگنال pre_save برای پاک کردن فایل قدیمی
# -----------------------------
def delete_old_file(field_name, default_name=None):
    def inner(sender, instance, **kwargs):
        if not instance.pk:
            return  # instance تازه ایجاد شده
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)
        if old_file and old_file != new_file and old_file.name != default_name:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
            remove_folder_if_empty(old_file)
    return inner

pre_save.connect(delete_old_file('cat_img', 'di_categury.jpg'), sender=Categury)
pre_save.connect(delete_old_file('product_img', 'di_cook.png'), sender=Product)
pre_save.connect(delete_old_file('image', 'di_course.png'), sender=Course)
pre_save.connect(delete_old_file('video'), sender=Course)  # اگر ویدئو تغییر کرد پاک شود
pre_save.connect(delete_old_file('profile_img', 'dp_image.jpg'), sender=CustomUser)
