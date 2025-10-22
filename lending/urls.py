from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import LendingConfig
from .views import LendingRecordViewSet

app_name = LendingConfig.name

router = DefaultRouter()
router.register(r"lendings", LendingRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
] + router.urls
