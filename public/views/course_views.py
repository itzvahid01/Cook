# public/views/course_views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import watson
from django.db.models import Count, Avg
from ..models import Course
from ..serializers import CourseSerializer, CourseDetailSerializer, CourseListSerializer
from ..filters import CourseFilter
from rest_framework.pagination import CursorPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from public.serializers.course_serializers import CourseInfiniteScrollSerializer

class CourseInfinitePagination(CursorPagination):
    page_size = 15
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'has_next': bool(self.get_next_link()),
            'has_previous': bool(self.get_previous_link()),
            'count': len(data),
            'results': data
        })
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    اجازه می‌دهد:
    - همه کاربران (حتی بدون لاگین) متدهای ایمن (GET, HEAD, OPTIONS) را اجرا کنند
    - فقط معلمان و staff بتوانند ایجاد، ویرایش و حذف کنند
    """
    
    def has_permission(self, request, view):
        # اگر درخواست فقط برای خواندن است، همه اجازه دارند
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # برای درخواست‌های غیرایمن (POST, PUT, DELETE, PATCH)
        # باید کاربر احراز هویت شده باشد و معلم یا staff باشد
        if not request.user or not request.user.is_authenticated:
            return False
        
        # بررسی وجود ویژگی is_teacher به صورت ایمن
        return hasattr(request.user, 'is_teacher') and (
            request.user.is_teacher or request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        """
        برای بررسی دسترسی به یک شیء خاص
        """
        # اگر درخواست فقط برای خواندن است، همه اجازه دارند
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # برای درخواست‌های غیرایمن، بررسی مالکیت
        if not request.user or not request.user.is_authenticated:
            return False
        
        # اگر کاربر staff است، اجازه دارد
        if request.user.is_staff:
            return True
        
        # بررسی اینکه آیا کاربر معلم است و مالک دوره است
        return (
            hasattr(request.user, 'is_teacher') and 
            request.user.is_teacher and 
            obj.teacher_id == request.user
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]
    lookup_field = 'slug'
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    
    search_fields = [
        'title',
        'description',
        'market_description',
        'teacher_id__name',
        'teacher_id__family',
        'course_type__title'
    ]
    
    ordering_fields = [
        'price', 'finaly_price', 'duration', 'start_date',
        'created_at', 'update_at', 'discount', 'total_capacity'
    ]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('teacher_id', 'course_type')
        
        if self.request.user.is_authenticated and self.request.user.is_teacher:
            if self.request.query_params.get('my_courses'):
                queryset = queryset.filter(teacher_id=self.request.user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def perform_create(self, serializer):
        if self.request.user.is_teacher:
            serializer.save(teacher_id=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """جستجوی پیشرفته با watson"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'error': 'پارامتر جستجو الزامی است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        search_results = watson.search(query, models=(Course,))
        
        queryset = Course.objects.filter(id__in=[obj.object_id for obj in search_results])
        
        # اعمال فیلترهای دیگر
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        class_type = request.query_params.get('class_type')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if class_type:
            queryset = queryset.filter(class_type=class_type)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """جستجوی خودکار برای پیشنهادات"""
        query = request.query_params.get('q', '')
        
        if not query or len(query) < 2:
            return Response({'suggestions': []})
        
        search_results = watson.search(query, models=(Course,))
        
        suggestions = []
        for result in search_results[:10]:
            suggestions.append({
                'id': result.object_id,
                'title': result.title,
                'description': result.description[:100] + '...' if len(result.description) > 100 else result.description,
                'url': f'/courses/{result.meta["slug"]}/' if 'slug' in result.meta else f'/courses/{result.object_id}/',
                'type': 'course'
            })
        
        return Response({'suggestions': suggestions})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار دوره‌ها"""
        from django.db.models import Sum  # ✅ import درون تابع
        
        stats = {
            'total_courses': Course.objects.count(),
            'online_courses': Course.objects.filter(class_type='online').count(),
            'in_person_courses': Course.objects.filter(class_type='in_person').count(),
            'courses_with_certificate': Course.objects.filter(govahiname=True).count(),
            'available_courses': Course.objects.filter(available_seats__gt=0).count(),
            'full_courses': Course.objects.filter(available_seats=0).count(),
            'average_price': Course.objects.aggregate(Avg('price'))['price__avg'] or 0,
            'average_duration': Course.objects.aggregate(Avg('duration'))['duration__avg'] or 0,
        }
        
        # اضافه کردن Sum فقط اگر نیاز بود
        try:
            stats['total_capacity'] = Course.objects.aggregate(Sum('total_capacity'))['total_capacity__sum'] or 0
            stats['total_available'] = Course.objects.aggregate(Sum('available_seats'))['available_seats__sum'] or 0
        except:
            stats['total_capacity'] = 0
            stats['total_available'] = 0
        
        # آمار بر اساس دسته‌بندی
        category_stats = Course.objects.values(
            'course_type__title'
        ).annotate(
            count=Count('id'),
            avg_price=Avg('price')
        ).order_by('-count')
        
        stats['by_category'] = list(category_stats)
        
        return Response(stats)
    @action(detail=False, methods=['get'])
    def infinite_scroll(self, request):
        page_size = int(request.query_params.get('page_size', 10))
        offset = int(request.query_params.get('offset', 0))
        courses = Course.objects.all().order_by('-created_at')[offset:offset+page_size]
        serializer = CourseInfiniteScrollSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)