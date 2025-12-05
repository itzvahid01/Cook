# public/apps.py
from django.apps import AppConfig

class PublicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public'
    
    def ready(self):
        """این تابع هنگام راه‌اندازی Django اجرا می‌شود"""
        # import باید درون تابع باشد
        try:
            # روش درست import کردن watson
            from watson import search as watson_search
            from .models import Course, Product
            
            # ثبت مدل Course در watson
            watson_search.register(
                Course,
                fields=[
                    "title",
                    "description", 
                    "market_description",
                ],
                store=["teacher_id__name", "teacher_id__family", "course_type__title"]
            )
            
            # ثبت مدل Product در watson
            watson_search.register(
                Product,
                fields=["title", "description"],
                store=["tag__title", "tag__cat__title"]
            )
            
            print("✅ Watson models registered successfully")
            
        except ImportError as e:
            print(f"⚠️  Could not import watson: {e}")
        except Exception as e:
            print(f"⚠️  Error registering watson models: {e}")