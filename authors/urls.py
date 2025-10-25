from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authors.apps import AuthorsConfig
from authors.views import AuthorViewSet

app_name = AuthorsConfig.name

router = DefaultRouter()
router.register(r"authors", AuthorViewSet)

urlpatterns = [
    path("", include(router.urls)),
] + router.urls
