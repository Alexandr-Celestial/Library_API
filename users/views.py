from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class UserRegistrationAPIView(generics.CreateAPIView):
    """Контроллер для создания пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserDetailAPIView(generics.RetrieveAPIView):
    """Контроллер для получения информации о пользователе"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для обновления данных пользователя"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDeleteAPIView(generics.DestroyAPIView):
    """Контроллер для удаления текущего пользователя"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
