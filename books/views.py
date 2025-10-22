from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """Вьюсет для CRUD модели книги и поиск по различным критериям"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__full_name", "genre"]
