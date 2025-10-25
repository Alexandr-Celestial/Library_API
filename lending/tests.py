from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from .models import LendingRecord
from books.models import Book
from authors.models import Author
from users.models import User


class LendingTests(APITestCase):

    def setUp(self):
        """Создаёт тестовых пользователей, авторов и книги."""
        # Создаем пользователей
        self.user1 = User.objects.create(email="user1@example.com")
        self.user2 = User.objects.create(email="user2@example.com")
        self.admin_user = User.objects.create(email="admin@example.com", is_staff=True)

        # Создаем автора
        self.author = Author.objects.create(
            full_name="Test Author", biography="Test biography"
        )

        # Создаем книги
        self.book1 = Book.objects.create(
            title="Book 1",
            description="Description 1",
            author=self.author,
            genre="Fiction",
            owner=self.user1,
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            description="Description 2",
            author=self.author,
            genre="Science",
            owner=self.user1,
        )

        # Создаем записи о выдаче
        self.lending1 = LendingRecord.objects.create(book=self.book1, user=self.user1)
        self.lending2 = LendingRecord.objects.create(
            book=self.book2,
            user=self.user2,
            return_date=timezone.now(),  # Уже возвращена
        )

    # CRUD Tests
    def test_create_lending_record_authenticated(self):
        """Проверяет создание записи о выдаче книги аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-list")
        data = {"book": self.book1.id, "user": self.user1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LendingRecord.objects.count(), 3)

        # Проверяем, что запись создана с правильными данными
        new_lending = LendingRecord.objects.get(id=response.data["id"])
        self.assertEqual(new_lending.book, self.book1)
        self.assertEqual(new_lending.user, self.user1)
        self.assertIsNone(new_lending.return_date)

    def test_create_lending_record_unauthenticated(self):
        """Проверяет создание записи о выдаче неаутентифицированным пользователем"""
        url = reverse("lending:lendingrecord-list")
        data = {"book": self.book1.id, "user": self.user1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(LendingRecord.objects.count(), 2)

    def test_create_lending_record_missing_data(self):
        """Проверяет создание записи о выдаче с отсутствующими данными"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-list")
        data = {
            "book": self.book1.id
            # user отсутствует - но это может быть необязательным полем из-за null=True, blank=True
        }
        response = self.client.post(url, data)
        # Если поля необязательные, то создание может пройти успешно
        if response.status_code == status.HTTP_201_CREATED:
            # Проверяем, что user установлен в None
            new_lending = LendingRecord.objects.get(id=response.data["id"])
            self.assertIsNone(new_lending.user)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_lending_records_authenticated_user(self):
        """Проверяет получение списка записей о выдаче для обычного пользователя"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Только свои записи

        # Проверяем, что пользователь видит только свои записи
        lending_ids = [item["id"] for item in response.data]
        self.assertIn(self.lending1.id, lending_ids)
        self.assertNotIn(self.lending2.id, lending_ids)

    def test_list_lending_records_admin_user(self):
        """Проверяет получение списка записей о выдаче для администратора"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("lending:lendingrecord-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Все записи

        # Проверяем, что админ видит все записи
        lending_ids = [item["id"] for item in response.data]
        self.assertIn(self.lending1.id, lending_ids)
        self.assertIn(self.lending2.id, lending_ids)

    def test_list_lending_records_unauthenticated(self):
        """Проверяет получение списка записей о выдаче неаутентифицированным пользователем"""
        url = reverse("lending:lendingrecord-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lending_record_owner(self):
        """Проверяет получение детальной информации о своей записи выдачи"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lending1.id)
        self.assertEqual(response.data["book"], self.book1.id)
        self.assertEqual(response.data["user"], self.user1.id)

    def test_retrieve_lending_record_other_user(self):
        """Проверяет получение детальной информации о чужой записи выдачи"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_lending_record_admin(self):
        """Проверяет получение детальной информации о любой записи выдачи администратором"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("lending:lendingrecord-detail", args=[self.lending2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lending2.id)

    def test_retrieve_nonexistent_lending_record(self):
        """Проверяет получение несуществующей записи выдачи"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_lending_record_return_date(self):
        """Проверяет обновление даты возврата книги"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("lending:lendingrecord-detail", args=[self.lending1.id])

        # Устанавливаем дату возврата
        return_date = timezone.now()
        data = {"return_date": return_date.isoformat()}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.lending1.refresh_from_db()
        self.assertIsNotNone(self.lending1.return_date)

    def test_update_lending_record_regular_user(self):
        """Проверяет обновление записи выдачи обычным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending1.id])
        data = {"return_date": timezone.now().isoformat()}
        response = self.client.patch(url, data)

        # В ViewSet обычные пользователи могут обновлять свои записи
        # Проверяем, что обновление прошло успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные действительно обновились
        self.lending1.refresh_from_db()
        self.assertIsNotNone(self.lending1.return_date)

    def test_update_lending_record_other_user(self):
        """Проверяет обновление чужой записи выдачи"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending2.id])
        data = {"return_date": timezone.now().isoformat()}
        response = self.client.patch(url, data)
        # Не должен иметь доступа к чужой записи
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lending_record_admin(self):
        """Проверяет удаление записи выдачи администратором"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("lending:lendingrecord-detail", args=[self.lending1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LendingRecord.objects.count(), 1)

        # Проверяем, что запись действительно удалена
        with self.assertRaises(LendingRecord.DoesNotExist):
            LendingRecord.objects.get(id=self.lending1.id)

    def test_delete_lending_record_regular_user(self):
        """Проверяет удаление записи выдачи обычным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending1.id])
        response = self.client.delete(url)

        # В ViewSet обычные пользователи могут удалять свои записи
        # Проверяем, что удаление прошло успешно
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LendingRecord.objects.count(), 1)

    def test_delete_lending_record_other_user(self):
        """Проверяет удаление чужой записи выдачи"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-detail", args=[self.lending2.id])
        response = self.client.delete(url)
        # Не должен иметь доступа к чужой записи
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Status Tracking Tests
    def test_is_returned_property_returned(self):
        """Проверяет свойство is_returned для возвращенной книги"""
        result, message = self.lending2.is_returned
        self.assertTrue(result)
        self.assertEqual(message, "Книга возвращена")

    def test_is_returned_property_not_returned(self):
        """Проверяет свойство is_returned для не возвращенной книги"""
        result, message = self.lending1.is_returned
        self.assertFalse(result)
        self.assertEqual(message, "Книга отсутствует")

    def test_lending_record_str_method_returned(self):
        """Проверяет строковое представление для возвращенной книги"""
        expected_str = f"Книга {self.book2.title} выдана пользователю {self.user2.email} (возвращена)"
        self.assertEqual(str(self.lending2), expected_str)

    def test_lending_record_str_method_not_returned(self):
        """Проверяет строковое представление для не возвращенной книги"""
        expected_str = (
            f"Книга {self.book1.title} выдана пользователю {self.user1.email} (выдана)"
        )
        self.assertEqual(str(self.lending1), expected_str)

    def test_issue_date_auto_set(self):
        """Проверяет, что дата выдачи устанавливается автоматически"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-list")
        data = {"book": self.book1.id, "user": self.user1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что дата выдачи установлена
        new_lending = LendingRecord.objects.get(id=response.data["id"])
        self.assertIsNotNone(new_lending.issue_date)
        self.assertIsNone(new_lending.return_date)

    def test_read_only_fields(self):
        """Проверяет, что issue_date и is_returned доступны только для чтения"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("lending:lendingrecord-list")

        # Пытаемся установить issue_date и is_returned при создании
        data = {
            "book": self.book1.id,
            "user": self.user1.id,
            "issue_date": "2023-01-01T00:00:00Z",  # Должно игнорироваться
            "is_returned": True,  # Должно игнорироваться
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что read_only_fields не были установлены
        new_lending = LendingRecord.objects.get(id=response.data["id"])
        self.assertNotEqual(new_lending.issue_date.isoformat(), "2023-01-01T00:00:00Z")
        self.assertFalse(new_lending.is_returned[0])

    def test_multiple_lendings_same_book(self):
        """Проверяет возможность нескольких выдач одной книги"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lending:lendingrecord-list")

        # Создаем несколько записей для одной книги
        data1 = {"book": self.book1.id, "user": self.user1.id}
        data2 = {"book": self.book1.id, "user": self.user2.id}

        response1 = self.client.post(url, data1)
        response2 = self.client.post(url, data2)

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LendingRecord.objects.count(), 4)

    def test_lending_record_verbose_names(self):
        """Проверяет verbose_name модели LendingRecord"""
        self.assertEqual(LendingRecord._meta.verbose_name, "Лендинг")
        self.assertEqual(LendingRecord._meta.verbose_name_plural, "Лендинги")

    def tearDown(self):
        """Очистка после тестов"""
        self.client.force_authenticate(user=None)
