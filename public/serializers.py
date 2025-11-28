from rest_framework import serializers
from .models import CustomUser, Course, Order, Product, Order_Item, Payment, Enrollment,Categury

from rest_framework import serializers
from .models import CustomUser

from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    is_admin = serializers.SerializerMethodField(read_only=True)  # اضافه کردن فیلد ادمین

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'profile_img',
            'phone',
            'name',
            'family',
            'city',
            'address',
            'code_posti',
            'is_active',
            'password',
            'is_admin',  # اضافه شد
        ]
        read_only_fields = ['id', 'is_active', 'is_admin','phone']

    def get_is_admin(self, obj):
        # اگر مدل CustomUser فیلد is_staff یا is_superuser دارد:
        return getattr(obj, 'is_staff', False) or getattr(obj, 'is_superuser', False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CourseSerializer(serializers.ModelSerializer):
    teacher = CustomUserSerializer(read_only=True, source='teacher_id')
    
    class Meta:
        model = Course
        fields = ['id', 'teacher', 'title', 'description', 'price', 'duration', 'duration_type', 'start_date', 'finaly_price', 'discount']

class OrderSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'date', 'total_price', 'status']
from rest_framework import serializers
from public.models import Product
class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()  # متن تگ به جای ID
    url = serializers.SerializerMethodField()  # URL کامل محصول بر اساس slug

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'discount', 'stock',
                  'images', 'expiration_date', 'weight', 'tag', 'slug', 'url']

    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = []

        if obj.product_img and request:
            image_urls.append(request.build_absolute_uri(obj.product_img.url))

        for image in obj.images.all():
            if request:
                image_urls.append(request.build_absolute_uri(image.image.url))
            else:
                image_urls.append(image.image.url)

        return image_urls

    def get_tag(self, obj):
        # برگشت دادن متن تگ به جای ID
        return obj.tag.title if obj.tag else None

    def get_url(self, obj):
        # URL کامل محصول بر اساس slug
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, source='product_id')
    order = OrderSerializer(read_only=True, source='order_id')
    
    class Meta:
        model = Order_Item
        fields = ['id', 'order', 'product', 'quantity', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'order_date', 'status', 'refrence_number']

class EnrollmentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    course = CourseSerializer(read_only=True, source='course_id')
    
    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'enroll_date', 'payment_status']
from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'phone']

    def create(self, validated_data):
        # اینجا create_user خودش پسورد رو هش می‌کنه
        password = validated_data['password']
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=password,
            phone=validated_data['phone'],
            is_active=False  # تا شماره تایید نشه
        )
        return user
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['phone']
from rest_framework import serializers
from public.models import Categury

# Serializer برای لیست کتگوری‌ها (بدون products)
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


# Serializer برای جزئیات کتگوری (با products)
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
