# public/filters.py
import django_filters
from django.db.models import Q
import watson
from .models import Course, Product

class CourseFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_watson_search', label='جستجوی پیشرفته')
    
    # فیلترهای عددی
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='حداقل قیمت')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='حداکثر قیمت')
    
    # فیلترهای بولین
    has_certificate = django_filters.BooleanFilter(field_name='govahiname', label='دارای گواهینامه')
    available_only = django_filters.BooleanFilter(method='filter_available', label='فقط با ظرفیت خالی')
    
    # فیلترهای رابطه‌ای
    teacher = django_filters.CharFilter(field_name='teacher_id__name', lookup_expr='icontains', label='نام مدرس')
    category = django_filters.CharFilter(field_name='course_type__title', lookup_expr='icontains', label='دسته‌بندی')
    
    class Meta:
        model = Course
        fields = ['q', 'min_price', 'max_price', 'has_certificate', 
                 'available_only', 'class_type', 'teacher', 'category']
    
    def filter_watson_search(self, queryset, name, value):
        """جستجوی پیشرفته با watson"""
        if value:
            # استفاده از watson برای جستجوی full-text
            return watson.filter(queryset, value)
        return queryset
    
    def filter_available(self, queryset, name, value):
        """فیلتر بر اساس موجود بودن ظرفیت"""
        if value:
            return queryset.filter(available_seats__gt=0)
        return queryset

class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_watson_search', label='جستجوی پیشرفته')
    
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='حداقل قیمت')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='حداکثر قیمت')
    in_stock = django_filters.BooleanFilter(method='filter_stock', label='موجود در انبار')
    
    class Meta:
        model = Product
        fields = ['q', 'min_price', 'max_price', 'in_stock', 'tag']
    
    def filter_watson_search(self, queryset, name, value):
        """جستجوی پیشرفته با watson"""
        if value:
            return watson.filter(queryset, value)
        return queryset
    
    def filter_stock(self, queryset, name, value):
        """فیلتر موجودی"""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)