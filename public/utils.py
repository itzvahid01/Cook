import os
import string
import shutil
from django.utils.text import slugify
from django.conf import settings
import random

def get_bucket_folder(instance_id: int):
    """هر 100 تا محصول یک فولدر bucket جدا."""
    return (instance_id - 1) // 100 + 1


def get_product_folder(instance):
    """
    ساخت فولدر ثابت محصول — وابسته به id  
    نتیجه:  <slug>-<id>
    """
    slug = slugify(getattr(instance, "title", "item"), allow_unicode=True)
    return f"{slug}-{instance.id}"

def get_bucket_folder(instance_id):
    """هر 100 شی یک فولدر جدا"""
    return (instance_id - 1) // 100 + 1

def generate_folder_name(name, instance_id=None):
    """اسم فولدر: slug-title + id (اگر وجود داشت) + رشته رندوم"""
    slug = slugify(name, allow_unicode=True)
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    if instance_id:
        return f"{slug}-{instance_id}-{rand}"
    return f"{slug}-{rand}"

def build_media_path(prefix, instance=None, filename=None, **kwargs):
    """
    مسیر ذخیره‌سازی:
    prefix/img/<bucket>/<folder>/<filename>
    kwargs می‌تواند شامل title، teacher_name و ... باشد
    """

    # 1. پیدا کردن نام برای فولدر
    name = kwargs.get("title") or getattr(instance, "title", "item")
    instance_id = getattr(instance, "pk", None)

    folder_name = generate_folder_name(name, instance_id)

    # 2. تعیین bucket
    bucket = get_bucket_folder(instance_id or 1)

    # 3. مسیر نهایی
    return f"{prefix}/img/{bucket}/{folder_name}/{filename}"

def delete_product_folder(prefix, instance):
    """
    حذف فولدر محصول وقتی محصول پاک شد.
    """
    if not instance.pk:
        return

    bucket = get_bucket_folder(instance.pk)
    product_folder = get_product_folder(instance)

    folder_path = os.path.join(settings.MEDIA_ROOT, prefix, "img", str(bucket), product_folder)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
