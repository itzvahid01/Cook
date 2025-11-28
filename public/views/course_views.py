from rest_framework import viewsets, permissions
from ..models import Course
from ..serializers import CourseSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    فقط ادمین‌ها اجازه تغییر دارند، بقیه فقط مشاهده.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'