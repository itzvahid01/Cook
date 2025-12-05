# public/views/product_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import watson
from django.db.models import Count, Avg, Sum, Q  # ✅ اضافه کردن Sum
from ..models import Product
from ..serializers import ProductSerializer, ProductDetailSerializer, ProductListSerializer
from ..filters import ProductFilter
from .course_views import IsAdminOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    
    search_fields = ['title', 'description', 'tag__title', 'tag__cat__title']
    
    ordering_fields = ['price', 'discount', 'stock', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.all()
        queryset = queryset.select_related('tag', 'tag__cat')
        queryset = queryset.prefetch_related('images')
        
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        in_stock = self.request.query_params.get('in_stock')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock__gt=0)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(stock=0)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """جستجوی پیشرفته محصولات"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'error': 'پارامتر جستجو الزامی است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        search_results = watson.search(query, models=(Product,))
        
        queryset = Product.objects.filter(id__in=[obj.object_id for obj in search_results])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار محصولات"""
        from django.db.models import Sum  # ✅ import درون تابع
        
        stats = {
            'total_products': Product.objects.count(),
            'in_stock': Product.objects.filter(stock__gt=0).count(),
            'out_of_stock': Product.objects.filter(stock=0).count(),
            'with_discount': Product.objects.filter(discount__gt=0).count(),
            'average_price': Product.objects.aggregate(Avg('price'))['price__avg'] or 0,
        }
        
        # اضافه کردن Sum
        try:
            stats['total_stock'] = Product.objects.aggregate(Sum('stock'))['stock__sum'] or 0
        except:
            stats['total_stock'] = 0
        
        # آمار بر اساس دسته‌بندی
        category_stats = Product.objects.values(
            'tag__cat__title'
        ).annotate(
            count=Count('id'),
            avg_price=Avg('price')
        ).order_by('-count')
        
        stats['by_category'] = list(category_stats)
        
        return Response(stats)