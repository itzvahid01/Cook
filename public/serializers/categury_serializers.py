# public/serializers/categury_serializers.py
from rest_framework import serializers
from public.models import Categury, Product
from .product_serializers import ProductSerializer

# این کلاس برای course_serializers نیازه
class CategoryMiniSerializer(serializers.ModelSerializer):
    """نسخه ساده Category برای استفاده در Course"""
    class Meta:
        model = Categury
        fields = ['id', 'title', 'slug']

class CateguryListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Categury
        fields = ['title', 'cat_img', 'slug', 'url']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

class CateguryDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Categury
        fields = ['title', 'cat_img', 'url', 'products']
    
    def get_products(self, obj):
        request = self.context.get('request')
        products = Product.objects.filter(tag__cat=obj).order_by('-created_at')
        return ProductSerializer(products, many=True, context={'request': request}).data
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

# برای backward compatibility
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categury
        fields = '__all__'