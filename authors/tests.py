from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from authors.models import Author
from users.models import User


class AuthorTests(APITestCase):

    def setUp(self):
        """Создаёт тестового пользователя и авторов."""
        self.user = User.objects.create(email="testuser@example.com")
        self.author1 = Author.objects.create(
            full_name="Fyodor Dostoevsky",
            biography="Russian novelist, philosopher, and essayist",
        )
        self.author2 = Author.objects.create(
            full_name="Leo Tolstoy",
            biography="Russian writer regarded as one of the greatest authors of all time",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_author_authenticated(self):
        """Проверяет создание автора аутентифицированным пользователем"""
        url = reverse("authors:author-list")
        data = {
            "full_name": "Alexander Pushkin",
            "biography": "Russian poet, playwright, and novelist of the Romantic era",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(
            Author.objects.get(full_name="Alexander Pushkin").biography,
            "Russian poet, playwright, and novelist of the Romantic era",
        )

    def test_create_author_unauthenticated(self):
        """Проверяет создание автора неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("authors:author-list")
        data = {
            "full_name": "Alexander Pushkin",
            "biography": "Russian poet, playwright, and novelist of the Romantic era",
        }
        response = unauthenticated_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Author.objects.count(), 2)

    def test_create_author_invalid_data(self):
        """Проверяет создание автора с невалидными данными"""
        url = reverse("authors:author-list")
        data = {
            "full_name": "",  # Пустое имя - невалидные данные
            "biography": "Invalid author data",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Author.objects.count(), 2)

    def test_list_authors_authenticated(self):
        """Проверяет получение списка всех авторов аутентифицированным пользователем"""
        url = reverse("authors:author-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_authors_unauthenticated(self):
        """Проверяет получение списка всех авторов неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("authors:author-list")
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_author_authenticated(self):
        """Проверяет получение детальной информации об авторе аутентифицированным пользователем"""
        url = reverse("authors:author-detail", args=[self.author1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Fyodor Dostoevsky")
        self.assertEqual(
            response.data["biography"], "Russian novelist, philosopher, and essayist"
        )

    def test_retrieve_author_unauthenticated(self):
        """Проверяет получение детальной информации об авторе неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("authors:author-detail", args=[self.author1.id])
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_author(self):
        """Проверяет получение несуществующего автора"""
        url = reverse("authors:author-detail", args=[999])  # Несуществующий ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_author_authenticated(self):
        """Проверяет полное обновление автора аутентифицированным пользователем"""
        url = reverse("authors:author-detail", args=[self.author1.id])
        data = {
            "full_name": "Fyodor Mikhailovich Dostoevsky",
            "biography": "One of the most influential writers in world literature",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Fyodor Mikhailovich Dostoevsky")
        self.assertEqual(
            self.author1.biography,
            "One of the most influential writers in world literature",
        )

    def test_update_author_unauthenticated(self):
        """Проверяет обновление автора неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("authors:author-detail", args=[self.author1.id])
        data = {
            "full_name": "Fyodor Mikhailovich Dostoevsky",
            "biography": "Updated biography",
        }
        response = unauthenticated_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что данные не изменились
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Fyodor Dostoevsky")

    def test_partial_update_author(self):
        """Проверяет частичное обновление автора"""
        url = reverse("authors:author-detail", args=[self.author1.id])
        data = {"biography": "Updated biography with new information"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Fyodor Dostoevsky")
        self.assertEqual(
            self.author1.biography, "Updated biography with new information"
        )

    def test_update_author_invalid_data(self):
        """Проверяет обновление автора с невалидными данными"""
        url = reverse("authors:author-detail", args=[self.author1.id])
        data = {
            "full_name": "",  # Пустое имя - невалидные данные
            "biography": "Invalid author data",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Проверяем, что данные не изменились
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Fyodor Dostoevsky")

    def test_update_nonexistent_author(self):
        """Проверяет обновление несуществующего автора"""
        url = reverse("authors:author-detail", args=[999])  # Несуществующий ID
        data = {
            "full_name": "Alexander Pushkin",
            "biography": "Russian poet, playwright, and novelist of the Romantic era",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_author_authenticated(self):
        """Проверяет удаление автора аутентифицированным пользователем"""
        url = reverse("authors:author-detail", args=[self.author1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 1)

        # Проверяем, что автор действительно удален
        with self.assertRaises(Author.DoesNotExist):
            Author.objects.get(id=self.author1.id)

    def test_delete_author_unauthenticated(self):
        """Проверяет удаление автора неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("authors:author-detail", args=[self.author1.id])
        response = unauthenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Author.objects.count(), 2)

    def test_delete_nonexistent_author(self):
        """Проверяет удаление несуществующего автора"""
        url = reverse("authors:author-detail", args=[999])  # Несуществующий ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Author.objects.count(), 2)
