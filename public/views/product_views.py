# views.py
from rest_framework import viewsets
from public.models import Product
from public.serializers import ProductSerializer
from .course_views import IsAdminOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'  # برای URL فارسی
    queryset = Product.objects.all().order_by('-created_at')
