from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        """Создаёт тестовых пользователей."""
        self.user1 = User.objects.create(email="user1@example.com")
        self.user2 = User.objects.create(email="user2@example.com")

        # Устанавливаем пароли для пользователей
        self.user1.set_password("testpassword123")
        self.user2.set_password("testpassword456")
        self.user1.save()
        self.user2.save()

    # Registration Tests
    def test_user_registration_success(self):
        """Проверяет успешную регистрацию пользователя"""
        url = reverse("users:user_register")
        data = {"email": "newuser@example.com", "password": "newpassword123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

        # Проверяем, что пользователь создан
        new_user = User.objects.get(email="newuser@example.com")
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.check_password("newpassword123"))

    def test_user_registration_duplicate_email(self):
        """Проверяет регистрацию с уже существующим email"""
        url = reverse("users:user_register")
        data = {
            "email": "user1@example.com",  # Уже существует
            "password": "password123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_invalid_email(self):
        """Проверяет регистрацию с невалидным email"""
        url = reverse("users:user_register")
        data = {"email": "invalid-email", "password": "password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_missing_password(self):
        """Проверяет регистрацию без пароля"""
        url = reverse("users:user_register")
        data = {
            "email": "newuser@example.com",
            # password отсутствует
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_missing_email(self):
        """Проверяет регистрацию без email"""
        url = reverse("users:user_register")
        data = {
            "password": "password123"
            # email отсутствует
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    # Authentication Tests (JWT)
    def test_jwt_token_obtain_success(self):
        """Проверяет успешное получение JWT токена"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "user1@example.com", "password": "testpassword123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_token_obtain_invalid_credentials(self):
        """Проверяет получение токена с неверными учетными данными"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "user1@example.com", "password": "wrongpassword"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_obtain_nonexistent_user(self):
        """Проверяет получение токена для несуществующего пользователя"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "nonexistent@example.com", "password": "password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh_success(self):
        """Проверяет успешное обновление JWT токена"""
        # Сначала получаем refresh token
        refresh = RefreshToken.for_user(self.user1)

        url = reverse("users:token_refresh")
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_jwt_token_refresh_invalid(self):
        """Проверяет обновление с невалидным refresh токеном"""
        url = reverse("users:token_refresh")
        data = {"refresh": "invalid-refresh-token"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # User Profile Tests
    def test_get_user_profile_authenticated(self):
        """Проверяет получение профиля аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("users:user_detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user1@example.com")
        self.assertEqual(response.data["id"], self.user1.id)

    def test_get_user_profile_unauthenticated(self):
        """Проверяет получение профиля неаутентифицированным пользователем"""
        url = reverse("users:user_detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_authenticated(self):
        """Проверяет обновление профиля аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("users:user_update")
        data = {"email": "updated@example.com"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "updated@example.com")

    def test_update_user_profile_unauthenticated(self):
        """Проверяет обновление профиля неаутентифицированным пользователем"""
        url = reverse("users:user_update")
        data = {"email": "updated@example.com"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_duplicate_email(self):
        """Проверяет обновление профиля с уже существующим email"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("users:user_update")
        data = {"email": "user2@example.com"}  # Email другого пользователя
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Проверяем, что данные не изменились
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "user1@example.com")

    def test_update_user_profile_invalid_email(self):
        """Проверяет обновление профиля с невалидным email"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("users:user_update")
        data = {"email": "invalid-email"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_account_authenticated(self):
        """Проверяет удаление аккаунта аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("users:user_delete")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)

        # Проверяем, что пользователь действительно удален
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user1.id)

    def test_delete_user_account_unauthenticated(self):
        """Проверяет удаление аккаунта неаутентифицированным пользователем"""
        url = reverse("users:user_delete")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 2)

    # Additional Tests
    def test_user_str_method(self):
        """Проверяет строковое представление модели User"""
        user = User.objects.create(email="test@example.com")
        self.assertEqual(str(user), "test@example.com")

    def test_user_model_verbose_names(self):
        """Проверяет verbose_name модели User"""
        self.assertEqual(User._meta.verbose_name, "Пользователь")
        self.assertEqual(User._meta.verbose_name_plural, "Пользователи")

    def test_user_unique_email_constraint(self):
        """Проверяет уникальность email"""
        with self.assertRaises(
            Exception
        ):  # Может быть IntegrityError или ValidationError
            User.objects.create(email="user1@example.com")

    def test_user_authentication_flow(self):
        """Проверяет полный цикл аутентификации: регистрация -> логин -> доступ к профилю"""
        # 1. Регистрация
        register_url = reverse("users:user_register")
        register_data = {"email": "flowtest@example.com", "password": "flowpassword123"}
        register_response = self.client.post(register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. Получение токена
        token_url = reverse("users:token_obtain_pair")
        token_data = {"email": "flowtest@example.com", "password": "flowpassword123"}
        token_response = self.client.post(token_url, token_data)
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        access_token = token_response.data["access"]

        # 3. Доступ к профилю с токеном
        profile_url = reverse("users:user_detail")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get(profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["email"], "flowtest@example.com")

    def test_password_hashing(self):
        """Проверяет, что пароль хранится в хэшированном виде"""
        user = User.objects.create(email="hashtest@example.com")
        user.set_password("plainpassword")
        user.save()

        # Пароль не должен храниться в открытом виде
        self.assertNotEqual(user.password, "plainpassword")
        # Должен правильно проверяться
        self.assertTrue(user.check_password("plainpassword"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_optional_fields(self):
        """Проверяет создание пользователя с дополнительными полями"""
        url = reverse("users:user_register")
        data = {"email": "optional@example.com", "password": "password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="optional@example.com")
        # Исправленная проверка для ImageField
        self.assertFalse(user.avatar)  # Проверяем что поле пустое
        self.assertIsNone(user.phone_number)
        self.assertIsNone(user.city)

    def tearDown(self):
        """Очистка после тестов"""
        self.client.credentials()  # Сбрасываем аутентификацию
