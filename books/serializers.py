from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Book"""

    class Meta:
        model = Book
        fields = [
            "title",
            "description",
            "author",
            "genre",
            "published_date",
            "number_of_pages",
            "owner",
        ]
