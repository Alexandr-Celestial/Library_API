from rest_framework import serializers

from lending.models import LendingRecord


class LendingRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для отслеживания выдачи книг"""

    class Meta:
        model = LendingRecord
        fields = ["id", "book", "user", "issue_date", "return_date", "is_returned"]
        read_only_fields = ["issue_date", "is_returned"]
