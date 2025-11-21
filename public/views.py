from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
import random, datetime

from .models import CustomUser, Course, Order, Product, Order_Item, Payment, Enrollment
from .serializers import (
    CustomUserSerializer, CourseSerializer, OrderSerializer,
    ProductSerializer, OrderItemSerializer, PaymentSerializer,
    EnrollmentSerializer, RegisterSerializer
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # بلاک کردن توکن
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# ---------- Custom Permissions ----------
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    فقط ادمین‌ها اجازه تغییر دارند، بقیه فقط مشاهده.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

# ---------- User Views ----------
class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران لاگین‌شده
    queryset = CustomUser.objects.all()

    def get_queryset(self):
        # کاربر فقط خودش را می‌تواند ببیند
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

# ---------- Models Views (Courses, Products, Orders, ...) ----------
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

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

# ---------- Registration ----------
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "ثبت نام موفقیت آمیز بود"},
            status=status.HTTP_201_CREATED
        )

# ---------- Phone Verification ----------
@api_view(['POST'])
def verify_number(request):
    number = request.data.get('number')
    code = request.data.get('code')
    try:
        user = CustomUser.objects.get(number=number)
        if code == "1234":
            user.is_active = True
            user.save()
            return Response({"status": "verified"})
        return Response({"status": "wrong code"}, status=400)
    except CustomUser.DoesNotExist:
        return Response({"status": "not found"}, status=404)

#---------- Home ------------

@api_view(['GET'])
def checklogin(request):
    user = request.user

    if user.is_authenticated:
        data = {
            "is_active": True,
            "name": user.name,
            "family": user.family,
            "profile_image": request.build_absolute_uri(user.profile_img.url) if user.profile_img else None
        }
    else:
        # اگر کاربر لاگین نکرده
        data = {
            "is_active": False,
            "name": None,
            "family": None,
            "profile_image": None
        }

    return Response(data, status=status.HTTP_200_OK)
# ---------- Code-based Login / Register ----------
codes = {}  # نگهداری کدها با زمان ثبت
CODE_EXPIRY_MINUTES = 2

class CodeCheckBase(APIView):
    """ کلاس پایه برای ارسال و بررسی کد """
    def handle_code(self, phone, code):
        now = datetime.datetime.now()

        if not code:
            code = str(random.randint(1000, 9999))
            codes[phone] = {"code": code, "time": now}
            return Response({"message": "کد ارسال شد", "code": code}, status=status.HTTP_200_OK)

        stored = codes.get(phone)
        if stored:
            elapsed = (now - stored["time"]).total_seconds() / 60
            if elapsed > CODE_EXPIRY_MINUTES:
                codes.pop(phone)
                return Response({"success": False, "message": "کد منقضی شده است!"}, status=status.HTTP_400_BAD_REQUEST)
            if stored["code"] == code:
                user, created = CustomUser.objects.get_or_create(phone=phone)
                codes.pop(phone, None)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "success": True,
                    "message": "کاربر با موفقیت وارد شد." if not created else "کاربر جدید ساخته شد.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=201)
        return Response({"success": False, "message": "کد اشتباه است!"}, status=status.HTTP_400_BAD_REQUEST)

class CodeCheckR(CodeCheckBase):
    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        code = request.data.get("code")
        if not phone:
            return Response({"error": "شماره موبایل الزامی است"}, status=status.HTTP_400_BAD_REQUEST)
        return self.handle_code(phone, code)

class CodeCheckL(CodeCheckBase):
    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        code = request.data.get("code")
        if not phone:
            return Response({"error": "شماره موبایل الزامی است"}, status=status.HTTP_400_BAD_REQUEST)
        return self.handle_code(phone, code)
