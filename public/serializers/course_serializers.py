# public/serializers/course_serializers.py
from rest_framework import serializers
from public.models import Course
from django.utils.functional import lazy
# به course_serializers.py اضافه کنید:
class CourseSerializer(serializers.ModelSerializer):
    """سریالایزر پایه برای دوره"""
    teacher = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'update_at']
    
    def get_teacher(self, obj):
        if obj.teacher_id:
            return {
                'id': obj.teacher_id.id,
                'name': obj.teacher_full_name
            }
        return None
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()
class CourseListSerializer(serializers.ModelSerializer):
    # فیلدهای ساده
    category_name = serializers.CharField(source='course_type.title', read_only=True)

    # فیلدهای lazy
    teacher_name = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  # اضافه شده

    # فیلدهای شرطی (فقط هنگام نیاز)
    stats = serializers.SerializerMethodField()
    detailed_info = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'price', 'category_name',
            'duration', 'start_date', 'image_url', 'class_type',
            'govahiname', 'total_capacity',
            'teacher_name', 'final_price', 'available_seats',
            'is_full', 'url', 'created_at',
            'stats', 'detailed_info'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher_full_name

    def get_final_price(self, obj):
        return obj.final_price

    def get_available_seats(self, obj):
        return obj.available_seats

    def get_is_full(self, obj):
        return obj.is_full

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

    def get_stats(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_stats') == 'true':
            return obj.enrollment_stats
        return None

    def get_detailed_info(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return {
                'can_enroll': obj.available_seats > 0,
                'market_description_preview': obj.market_description[:100] if obj.market_description else ''
            }
        return None


class CourseDetailSerializer(serializers.ModelSerializer):
    # Relation‌ها را lazy کنیم
    teacher_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    
    # فیلدهای lazy
    url = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    can_enroll = serializers.SerializerMethodField()
    enrollment_stats = serializers.SerializerMethodField()
    
    # فیلدهای سنگین - فقط هنگام نیاز
    full_syllabus = serializers.SerializerMethodField()
    detailed_prerequisites = serializers.SerializerMethodField()
    related_courses = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'price',
            'duration', 'start_date', 'image', 'video',
            'teacher_info', 'category_info', 'url',
            'total_capacity', 'class_type', 'govahiname',
            'market_description', 'syllabus', 'prerequisites',
            'acquired_skills', 'created_at', 'update_at',
            'is_full', 'can_enroll', 'enrollment_stats',
            'full_syllabus', 'detailed_prerequisites', 'related_courses'
        ]
    def get_teacher_name(self, obj):
        """Lazy property از مدل با error handling"""
        try:
            return obj.teacher_full_name
        except AttributeError:
            return "ناشناس"
        except Exception:
            return "خطا در دریافت اطلاعات"
    def get_teacher_info(self, obj):
        """Lazy loading اطلاعات استاد با cache بهتر"""
        cache_key = f"teacher_info_{obj.teacher_id_id}_{obj.id}"
        
        if not hasattr(self, '_teacher_info_cache'):
            self._teacher_info_cache = {}
        
        if cache_key not in self._teacher_info_cache:
            from .user_serializers import TeacherMiniSerializer
            self._teacher_info_cache[cache_key] = TeacherMiniSerializer(
                obj.teacher_id, 
                context=self.context
            ).data
        
        return self._teacher_info_cache[cache_key]
    
    def get_category_info(self, obj):
        """Lazy loading اطلاعات دسته‌بندی"""
        if not hasattr(self, '_category_info_cache'):
            from .categury_serializers import CategoryMiniSerializer
            self._category_info_cache = CategoryMiniSerializer(
                obj.course_type,
                context=self.context
            ).data
        return self._category_info_cache
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()
    
    def get_is_full(self, obj):
        return obj.is_full
    
    def get_can_enroll(self, obj):
        return obj.available_seats > 0
    
    def get_enrollment_stats(self, obj):
        return obj.enrollment_stats
    
    def get_full_syllabus(self, obj):
        """سرفصل کامل فقط هنگام درخواست"""
        request = self.context.get('request')
        if request and request.query_params.get('full_syllabus') == 'true':
            return lazy(lambda: self._parse_syllabus(obj.syllabus), list)()
        return None
    
    def get_detailed_prerequisites(self, obj):
        """پیش‌نیازهای کامل"""
        request = self.context.get('request')
        if request and request.query_params.get('detailed_prereq') == 'true':
            return lazy(lambda: self._expand_prerequisites(obj.prerequisites), list)()
        return obj.prerequisites[:200] + '...' if obj.prerequisites and len(obj.prerequisites) > 200 else obj.prerequisites
    
    def get_related_courses(self, obj):
        """دوره‌های مرتبط - lazy query"""
        request = self.context.get('request')
        if request and request.query_params.get('related_courses') == 'true':
            return lazy(self._get_related_courses, list)(obj)
        return None
    
    def _parse_syllabus(self, syllabus_text):
        """پارس سرفصل - محاسبات سنگین"""
        # منطق سنگین پارس کردن
        return syllabus_text.split('\n') if syllabus_text else []
    
    def _expand_prerequisites(self, prereq_text):
        """گسترش پیش‌نیازها"""
        # منطق سنگین
        return prereq_text
    
    def _get_related_courses(self, obj):
        """دریافت دوره‌های مرتبط - lazy query"""
        from .course_serializers import CourseInfiniteScrollSerializer  # یا یک سریالایزر سبک
        
        related = Course.objects.filter(
            course_type=obj.course_type
        ).exclude(id=obj.id)[:5]
        
        # استفاده از یک سریالایزر سبک‌تر
        return CourseInfiniteScrollSerializer(related, many=True, context=self.context).data
class CourseInfiniteScrollSerializer(serializers.ModelSerializer):
    """سریالایزر فوق سبک برای infinite scroll"""
    teacher_name = serializers.SerializerMethodField()
    category = serializers.CharField(source='course_type.title', read_only=True)
    image_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'image_url',
            'price', 'discount','total_capacity',
            'duration', 'teacher_name', 'category','available_seats',
            'class_type', 'start_date','govahiname','url'
        ]
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()
    
    def get_teacher_name(self, obj):
        """فقط نام استاد"""
        if obj.teacher_id:
            return f"{getattr(obj.teacher_id, 'name', '')} {getattr(obj.teacher_id, 'family', '')}".strip() or obj.teacher_id.phone
        return None
    
    def get_image_url(self, obj):
        """URL تصویر"""
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None