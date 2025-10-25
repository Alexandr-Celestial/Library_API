from django.db import models


class Author(models.Model):
    """Модель Автора"""

    full_name = models.CharField(
        max_length=100, verbose_name="Имя автора", null=False, blank=False
    )
    biography = models.TextField(verbose_name="Биография", null=False, blank=False)

    def __str__(self):
        return f"Автор {self.full_name} с биографией '{self.biography}'"

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
