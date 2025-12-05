from django.core.management.base import BaseCommand
from public.models import Product, ProductImage, Tag, Categury, Course
from public.models.user_model import CustomUser
import random
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create test products, categories, tags, courses, and teacher users'

    def handle(self, *args, **kwargs):
        Categury.objects.all().delete()
        categories = []
        for i in range(1, 6):
            cat_title = f"کتگوری تستی {i}"
            category, _ = Categury.objects.get_or_create(title=cat_title)
            categories.append(category)

        Tag.objects.all().delete()
        tags = []
        for category in categories:
            for j in range(1, 4):
                tag_title = f"تگ {category.title}-{j}"
                tag, _ = Tag.objects.get_or_create(title=tag_title, cat=category)
                tags.append(tag)

        CustomUser.objects.all().delete()
        teachers = []
        if not teachers:
            for i in range(1, 6):  # ساخت 5 کاربر تستی
                phone_number = f'09123456{i:03d}'  # شماره تلفن 11 رقمی
                teacher = CustomUser.objects.create_user(
                    phone=phone_number,
                    password='123456',
                    name = f'علی{i:03d}',
                    family = f'عباسی{i:03d}'
                )
                teachers.append(teacher)
                self.stdout.write(self.style.SUCCESS(f'Teacher user created: {teacher.phone}'))

        Course.objects.all().delete()
        courses = []
        for i in range(1, 51):
            course_title = f"کورس تستی {i}"
            course_description = f"توضیحات کورس شماره {i}"
            duration = random.randint(5, 20)
            start_date = date.today() + timedelta(days=random.randint(1, 30))
            price = random.randint(500, 5000)
            teacher = random.choice(teachers)
            course_type = random.choice(categories + [None])  # اختیاری
            # 1. ساخت تصویر
            image = Image.new(
                'RGB',
                (600, 400),
                color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            )

            # 2. ذخیره تصویر در buffer
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)  # مهم: بازگشت به ابتدای buffer

            # 3. تبدیل buffer به ContentFile
            image_file = ContentFile(buffer.getvalue(), name=f"course_{i}.png")

            # 4. ساخت دوره بدون تصویر اولیه
            course = Course.objects.create(
                teacher_id=teacher,
                course_type=course_type,
                title=course_title,
                description=course_description,
                price=price,
                govahiname=random.choice([True,False]),
                duration=duration,
                total_capacity=random.randint(10,50),
                start_date=start_date,
                finaly_price=max(0, price - random.randint(0, 200)),
                discount=random.choice([0, 5, 10, 15])
                # ❌ image را اینجا نذار
            )

            # 5. حالا تصویر را ذخیره کنید
            course.image.save(f"course_{i}.png", image_file, save=True)
            courses.append(course)
            self.stdout.write(self.style.SUCCESS(
                f"Course created: {course.title} | slug: {course.slug} | Teacher: {teacher.phone}"
            ))

        Product.objects.all().delete()
        for i in range(1, 51):
            title = f"محصول تستی {i}"
            description = f"توضیحات محصول تستی شماره {i}"
            price = random.randint(100, 1000)
            discount = random.choice([0, 5, 10, 15])
            stock = random.randint(1, 100)
            weight = random.randint(100, 1000)
            expiration_date = random.randint(5, 50)
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
            image = Image.new(
                'RGB',
                (600, 400),
                color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            )
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            product_image = ProductImage(product=product)
            product_image.image.save(f"product_{i}.png", ContentFile(buffer.getvalue()), save=True)
