# public/serializers/product_serializers.py
from rest_framework import serializers
from public.models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    tag_name = serializers.CharField(source='tag.title', read_only=True)
    category_name = serializers.CharField(source='tag.cat.title', read_only=True)
    final_price = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'discount', 'final_price',
            'stock', 'weight', 'expiration_date', 'images', 'tag_name',
            'category_name', 'url', 'created_at'
        ]
    
    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = []
        
        if obj.product_img and request:
            image_urls.append(request.build_absolute_uri(obj.product_img.url))
        
        for image in obj.images.all()[:3]:
            if request and image.image:
                image_urls.append(request.build_absolute_uri(image.image.url))
        
        return image_urls
    
    def get_final_price(self, obj):
        if obj.discount > 0:
            return obj.price * (100 - obj.discount) // 100
        return obj.price
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    tag_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'discount',
            'final_price', 'discount_percentage', 'stock', 'weight',
            'expiration_date', 'images', 'tag_info', 'category_info',
            'is_in_stock', 'url', 'created_at', 'update_at'
        ]
    
    def get_tag_info(self, obj):
        if obj.tag:
            return {
                'id': obj.tag.id,
                'title': obj.tag.title
            }
        return None
    
    def get_category_info(self, obj):
        if obj.tag and obj.tag.cat:
            return {
                'id': obj.tag.cat.id,
                'title': obj.tag.cat.title,
                'slug': obj.tag.cat.slug
            }
        return None
    
    def get_final_price(self, obj):
        if obj.discount > 0:
            return obj.price * (100 - obj.discount) // 100
        return obj.price
    
    def get_discount_percentage(self, obj):
        return obj.discount
    
    def get_is_in_stock(self, obj):
        return obj.stock > 0
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'update_at']