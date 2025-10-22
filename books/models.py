from django.db import models
from django.db.models import CASCADE

from authors.models import Author
from users.models import User


class Book(models.Model):
    """Модель книги"""

    title = models.CharField(
        max_length=150, verbose_name="Оглавление", null=True, blank=True
    )
    description = models.CharField(
        max_length=400, verbose_name="Описание", null=True, blank=True
    )
    author = models.ForeignKey(
        Author, verbose_name="Автор", on_delete=CASCADE, null=True, blank=True
    )
    genre = models.CharField(max_length=100, verbose_name="Жанр", null=True, blank=True)
    published_date = models.DateField(
        verbose_name="Дата публикации", null=True, blank=True
    )
    number_of_pages = models.IntegerField(
        verbose_name="Количество страниц", null=True, blank=True
    )
    owner = models.ForeignKey(
        User, verbose_name="Владелец", on_delete=CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Книга {self.title} автор {self.author} жанр {self.genre}"

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
