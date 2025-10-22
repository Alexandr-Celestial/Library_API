from rest_framework import viewsets, permissions
from .models import LendingRecord
from .serializers import LendingRecordSerializer


class LendingRecordViewSet(viewsets.ModelViewSet):
    """Вьюсет для отслеживания выдачи книг"""

    queryset = LendingRecord.objects.all()
    serializer_class = LendingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит только свои записи, админ — все
        user = self.request.user
        if user.is_staff:
            return LendingRecord.objects.all()
        return LendingRecord.objects.filter(user=user)
