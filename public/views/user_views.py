from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from ..models import CustomUser
from ..serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
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
