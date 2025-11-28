from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Course, Product
from ..serializers import CourseSerializer, ProductSerializer

# ---------- Custom Permission ----------
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    فقط صاحب شیء اجازه تغییر (PUT, PATCH, DELETE) دارد.
    GET و LIST برای صاحب و دیگران مجاز است.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user

# ---------- Staff Page ----------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_page(request):
    user = request.user
    if not user.is_staff:
        return Response({"error": "You are not staff / teacher"}, status=403)

    courses = Course.objects.filter(teacher=user)
    products = Product.objects.filter(teacher=user)

    return Response({
        "teacher": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "family": user.family,
            "profile_img": user.profile_img.url if user.profile_img else None
        },
        "courses": [{"id": c.id, "title": c.title, "price": c.price, "created_at": c.created_at} for c in courses],
        "products": [{"id": p.id, "title": p.title, "price": p.price, "created_at": p.created_at} for p in products]
    })

# ---------- Teacher ViewSets ----------
class TeacherCourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class TeacherProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
