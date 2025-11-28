from rest_framework import viewsets
from ..models import Order, Order_Item, Payment, Enrollment
from ..serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer, EnrollmentSerializer
from .course_views import IsAdminOrReadOnly  # Reuse permission

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = Order_Item.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminOrReadOnly]
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadOnly]
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrReadOnly]