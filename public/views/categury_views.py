# views.py
from rest_framework import viewsets
from public.models import Categury
from public.serializers import CateguryDetailSerializer,CateguryListSerializer
from .course_views import IsAdminOrReadOnly

class CateguryViewSet(viewsets.ModelViewSet):
    queryset = Categury.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':  # وقتی جزئیات یک کتگوری
            return CateguryDetailSerializer
        return CateguryListSerializer  # وقتی لیست کتگوری‌ها
