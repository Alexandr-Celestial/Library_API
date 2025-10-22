from rest_framework import serializers

from authors.models import Author


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Автора"""

    class Meta:
        model = Author
        fields = ["id", "full_name", "biography"]
