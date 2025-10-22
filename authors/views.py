from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from authors.models import Author
from authors.serializers import AuthorSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Автор"""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
