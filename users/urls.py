from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (
    UserRegistrationAPIView,
    UserDetailAPIView,
    UserUpdateAPIView,
    UserDeleteAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/register/", UserRegistrationAPIView.as_view(), name="user_register"),
    path("token/detail/", UserDetailAPIView.as_view(), name="user_detail"),
    path("token/update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("token/delete/", UserDeleteAPIView.as_view(), name="user_delete"),
]
