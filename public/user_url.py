from rest_framework import routers, permissions
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomUserViewSet, CourseViewSet, OrderViewSet, ProductViewSet,
    OrderItemViewSet, PaymentViewSet, EnrollmentViewSet,
    verify_number, CodeCheckR, CodeCheckL,checklogin,LogoutView
)

# ---------- Swagger ----------
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Documentation for my Django API",
        contact=openapi.Contact(email="youremail@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ---------- Router ----------
router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# مسیر اختصاصی برای کاربر فعلی
custom_user_view = CustomUserViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
})

# ---------- URLs ----------
urlpatterns = [
    # Swagger / Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # مسیر کاربر فعلی
    path('api/users/me/', custom_user_view, name='user-me'),

    # ثبت‌نام و ورود با کد
    path('api/register/', CodeCheckR.as_view(), name='register'),
    path('api/login/', CodeCheckL.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # JWT Token refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # بقیه ViewSet ها از طریق router
    path('api/', include(router.urls)),

    # اگر نیاز باشه شماره‌تایید معمولی هم اضافه بشه
    path('api/verify-number/', verify_number, name='verify-number'),
    #صفحه اصلی
    path('api/checklogin',checklogin,name='checklogin')
]
