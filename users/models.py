from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    username = None

    email = models.EmailField(
        unique=True,
        null=False,
        verbose_name="email",
        help_text="Введите адрес эл.почты",
    )
    avatar = models.ImageField(
        upload_to="avatar/", verbose_name="Аватар", null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=30, verbose_name="Номер телефона", null=True, blank=True
    )
    city = models.CharField(max_length=100, verbose_name="Город", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
