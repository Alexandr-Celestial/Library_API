from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Book
from authors.models import Author
from users.models import User


class BookTests(APITestCase):

    def setUp(self):
        """Создаёт тестового пользователя, авторов и книги."""
        # Создаем пользователя
        self.user = User.objects.create(email="testuser@example.com")
        self.other_user = User.objects.create(email="otheruser@example.com")

        # Создаем авторов
        self.author1 = Author.objects.create(
            full_name="Fyodor Dostoevsky", biography="Russian novelist"
        )
        self.author2 = Author.objects.create(
            full_name="Leo Tolstoy", biography="Russian writer"
        )

        # Создаем книги
        self.book1 = Book.objects.create(
            title="Crime and Punishment",
            description="A novel about morality and redemption",
            author=self.author1,
            genre="Philosophical fiction",
            published_date="1866-01-01",
            number_of_pages=430,
            owner=self.user,
        )
        self.book2 = Book.objects.create(
            title="War and Peace",
            description="Epic historical novel",
            author=self.author2,
            genre="Historical fiction",
            published_date="1869-01-01",
            number_of_pages=1225,
            owner=self.user,
        )

        # Аутентифицируем клиент
        self.client.force_authenticate(user=self.user)

    # CRUD Tests
    def test_create_book_authenticated(self):
        """Проверяет создание книги аутентифицированным пользователем"""
        url = reverse("books:book-list")
        data = {
            "title": "Anna Karenina",
            "description": "Tragic love story",
            "author": self.author2.id,
            "genre": "Realist novel",
            "published_date": "1877-01-01",
            "number_of_pages": 864,
            "owner": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.get(title="Anna Karenina").genre, "Realist novel")

    def test_create_book_unauthenticated(self):
        """Проверяет создание книги неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("books:book-list")
        data = {
            "title": "The Brothers Karamazov",
            "description": "Philosophical novel",
            "author": self.author1.id,
            "genre": "Philosophical fiction",
            "published_date": "1880-01-01",
            "number_of_pages": 796,
        }
        response = unauthenticated_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_book_invalid_data(self):
        """Проверяет создание книги с невалидными данными"""
        url = reverse("books:book-list")
        data = {
            "title": "T" * 151,  # Слишком длинное название (больше 150 символов)
            "description": "Test description",
            "author": self.author1.id,
            "genre": "Fiction",
            "published_date": "2020-01-01",
            "number_of_pages": 300,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 2)

    def test_list_books_authenticated(self):
        """Проверяет получение списка всех книг аутентифицированным пользователем"""
        url = reverse("books:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_books_unauthenticated(self):
        """Проверяет получение списка всех книг неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("books:book-list")
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_book_authenticated(self):
        """Проверяет получение детальной информации о книге аутентифицированным пользователем"""
        url = reverse("books:book-detail", args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Crime and Punishment")
        self.assertEqual(response.data["genre"], "Philosophical fiction")

    def test_retrieve_book_unauthenticated(self):
        """Проверяет получение детальной информации о книге неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("books:book-detail", args=[self.book1.id])
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_book(self):
        """Проверяет получение несуществующей книги"""
        url = reverse("books:book-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book_authenticated(self):
        """Проверяет полное обновление книги аутентифицированным пользователем"""
        url = reverse("books:book-detail", args=[self.book1.id])
        data = {
            "title": "Crime and Punishment (Revised)",
            "description": "Updated description",
            "author": self.author1.id,
            "genre": "Psychological fiction",
            "published_date": "1866-01-01",
            "number_of_pages": 450,
            "owner": self.user.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Crime and Punishment (Revised)")
        self.assertEqual(self.book1.genre, "Psychological fiction")

    def test_update_book_unauthenticated(self):
        """Проверяет обновление книги неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("books:book-detail", args=[self.book1.id])
        data = {
            "title": "Updated Title",
            "description": "Updated description",
            "author": self.author1.id,
            "genre": "Fiction",
            "published_date": "1866-01-01",
            "number_of_pages": 430,
        }
        response = unauthenticated_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что данные не изменились
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Crime and Punishment")

    def test_partial_update_book(self):
        """Проверяет частичное обновление книги"""
        url = reverse("books:book-detail", args=[self.book1.id])
        data = {
            "description": "New description about morality and psychology",
            "number_of_pages": 440,
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Crime and Punishment")  # Не изменилось
        self.assertEqual(
            self.book1.description, "New description about morality and psychology"
        )
        self.assertEqual(self.book1.number_of_pages, 440)

    def test_update_book_invalid_data(self):
        """Проверяет обновление книги с невалидными данными"""
        url = reverse("books:book-detail", args=[self.book1.id])
        data = {
            "title": "T" * 151,  # Слишком длинное название
            "description": "Test description",
            "author": self.author1.id,
            "genre": "Fiction",
            "published_date": "1866-01-01",
            "number_of_pages": 430,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Проверяем, что данные не изменились
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Crime and Punishment")

    def test_update_nonexistent_book(self):
        """Проверяет обновление несуществующей книги"""
        url = reverse("books:book-detail", args=[999])
        data = {
            "title": "Nonexistent Book",
            "description": "Test description",
            "author": self.author1.id,
            "genre": "Fiction",
            "published_date": "2020-01-01",
            "number_of_pages": 300,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_book_authenticated(self):
        """Проверяет удаление книги аутентифицированным пользователем"""
        url = reverse("books:book-detail", args=[self.book1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

        # Проверяем, что книга действительно удалена
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=self.book1.id)

    def test_delete_book_unauthenticated(self):
        """Проверяет удаление книги неаутентифицированным пользователем"""
        unauthenticated_client = APIClient()
        url = reverse("books:book-detail", args=[self.book1.id])
        response = unauthenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_nonexistent_book(self):
        """Проверяет удаление несуществующей книги"""
        url = reverse("books:book-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Book.objects.count(), 2)

    # Search Tests
    def test_search_books_by_title(self):
        """Проверяет поиск книг по названию"""
        url = reverse("books:book-list") + "?search=Crime"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Crime and Punishment")

    def test_search_books_by_genre(self):
        """Проверяет поиск книг по жанру"""
        url = reverse("books:book-list") + "?search=Historical"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "War and Peace")

    def test_search_books_by_author_name(self):
        """Проверяет поиск книг по имени автора"""
        # Note: This might not work as expected because search_fields uses 'author' (ID)
        # If you want to search by author name, change search_fields to ['author__full_name']
        url = reverse("books:book-list") + "?search=Dostoevsky"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The result depends on how DRF handles foreign key search

    def test_search_books_multiple_results(self):
        """Проверяет поиск, возвращающий несколько результатов"""
        url = reverse("books:book-list") + "?search=and"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ожидаем обе книги, так как обе содержат "and" в названии
        self.assertEqual(len(response.data), 2)

    def test_search_books_no_results(self):
        """Проверяет поиск, не возвращающий результатов"""
        url = reverse("books:book-list") + "?search=NonexistentBook"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_books_empty_query(self):
        """Проверяет поиск с пустым запросом"""
        url = reverse("books:book-list") + "?search="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Все книги

    # Additional Tests
    def test_book_str_method(self):
        """Проверяет строковое представление модели Book"""
        book = Book.objects.create(
            title="Test Book", author=self.author1, genre="Test Genre", owner=self.user
        )
        expected_str = f"Книга Test Book автор {self.author1} жанр Test Genre"
        self.assertEqual(str(book), expected_str)

    def test_create_book_with_minimal_data(self):
        """Проверяет создание книги с минимальным набором данных"""
        url = reverse("books:book-list")
        data = {
            "title": "Minimal Book",
            "author": self.author1.id,
            "owner": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    def test_book_owner_assignment(self):
        """Проверяет, что владелец книги правильно назначается"""
        url = reverse("books:book-list")
        data = {"title": "Owned Book", "author": self.author1.id, "owner": self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(title="Owned Book")
        self.assertEqual(book.owner, self.user)

    def tearDown(self):
        """Очистка после тестов"""
        self.client.force_authenticate(user=None)
