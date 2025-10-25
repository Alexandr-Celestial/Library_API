from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.apps import BooksConfig
from books.views import BookViewSet

app_name = BooksConfig.name

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
