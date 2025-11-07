from rest_framework import serializers
from .models import CustomUser, Course, Order, Product, Order_Item, Payment, Enrollment

from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phone',
            'name',
            'family',
            'city',
            'address',
            'code_posti',
            'email',
            'is_active',
            'password',
        ]
        read_only_fields = ['id', 'is_active']

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
from .models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)  # related_name در مدل ProductImage

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'finaly_price', 'discount', 'stock', 'main_image', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data[:3]:  # محدود به ۳ تصویر
            ProductImage.objects.create(product=product, **image_data)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data is not None:
            # حذف تصاویر قدیمی و اضافه کردن تصاویر جدید (حداکثر ۳)
            instance.images.all().delete()
            for image_data in images_data[:3]:
                ProductImage.objects.create(product=instance, **image_data)

        return instance

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
