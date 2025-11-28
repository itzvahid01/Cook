from django.core.management.base import BaseCommand
from public.models import Product, ProductImage, Tag, Categury
import random
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Create 50 test products with categories and tags'

    def handle(self, *args, **kwargs):
        # ایجاد کتگوری‌ها اگر وجود ندارند
        categories = []
        for i in range(1, 6):  # 5 کتگوری
            cat_title = f"کتگوری تستی {i}"
            category, _ = Categury.objects.get_or_create(title=cat_title)
            categories.append(category)

        # ایجاد تگ‌ها برای هر کتگوری
        tags = []
        for category in categories:
            for j in range(1, 4):  # 3 تگ در هر کتگوری
                tag_title = f"تگ {category.title}-{j}"
                tag, _ = Tag.objects.get_or_create(title=tag_title, cat=category)
                tags.append(tag)

        # ایجاد محصولات
        for i in range(1, 51):
            title = f"محصول تستی {i}"
            description = f"توضیحات محصول تستی شماره {i}"
            price = random.randint(100, 1000)
            discount = random.choice([0, 5, 10, 15])
            stock = random.randint(1, 100)
            weight = random.randint(100, 1000)
            expiration_date = random.randint(5, 50)

            # انتخاب تصادفی تگ
            tag = random.choice(tags)

            product = Product.objects.create(
                title=title,
                description=description,
                price=price,
                discount=discount,
                stock=stock,
                weight=weight,
                expiration_date=expiration_date,
                tag=tag
            )

            self.stdout.write(self.style.SUCCESS(
                f"Product created: {product.title} | slug: {product.slug} | Tag: {tag.title}"
            ))

            # ساخت تصویر تستی برای محصول (600x400)
            image = Image.new('RGB', (600, 400), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            product_image = ProductImage(
                product=product
            )
            product_image.image.save(f"product_{i}.png", ContentFile(buffer.getvalue()), save=True)
