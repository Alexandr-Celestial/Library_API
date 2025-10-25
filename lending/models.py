from django.conf import settings
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone

from books.models import Book


class LendingRecord(models.Model):
    """Модель для отслеживания выдачи книг"""

    book = models.ForeignKey(
        Book, on_delete=CASCADE, related_name="книга", null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="пользователь",
        null=True,
        blank=True,
    )
    issue_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(
        null=True, blank=True, help_text="Время возврата книги"
    )

    @property
    def is_returned(self):
        if self.return_date is not None:
            return True, "Книга возвращена"
        else:
            return False, "Книга отсутствует"

    def __str__(self):
        status = "возвращена" if self.return_date else "выдана"
        return (
            f"Книга {self.book.title} выдана пользователю {self.user.email} ({status})"
        )

    class Meta:
        verbose_name = "Лендинг"
        verbose_name_plural = "Лендинги"
