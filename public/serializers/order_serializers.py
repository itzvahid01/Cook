from rest_framework import serializers
from public.models import Order, Order_Item, Payment, Enrollment
from .user_serializers import CustomUserSerializer
from .product_serializers import ProductSerializer
from .course_serializers import CourseSerializer

class OrderSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    class Meta:
        model = Order
        fields = ['id','user','date','total_price','status']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, source='product_id')
    order = OrderSerializer(read_only=True, source='order_id')
    class Meta:
        model = Order_Item
        fields = ['id','order','product','quantity','price']

class PaymentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    class Meta:
        model = Payment
        fields = ['id','user','order_date','status','refrence_number']

class EnrollmentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True, source='user_id')
    course = CourseSerializer(read_only=True, source='course_id')
    class Meta:
        model = Enrollment
        fields = ['id','user','course','enroll_date','payment_status']
