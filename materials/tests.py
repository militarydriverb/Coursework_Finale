from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание пользователей
        self.user = User.objects.create(email="test@test.com")
        self.user.set_password("test123")
        self.user.save()

        self.other_user = User.objects.create(email="other@test.com")
        self.other_user.set_password("test123")
        self.other_user.save()

        # Создание курса
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )

        # Создание урока
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            video_url="https://www.youtube.com/watch?v=test",
            owner=self.user,
        )

    def test_lesson_list(self):
        """Тест получения списка уроков"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неаутентифицированным пользователем"""
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create(self):
        """Тест создания урока"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=new",
        }
        response = self.client.post(reverse("materials:lesson-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(response.data["name"], "New Lesson")

    def test_lesson_create_invalid_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course.id,
            "video_url": "https://www.vimeo.com/test",
        }
        response = self.client.post(reverse("materials:lesson-create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_retrieve(self):
        """Тест получения урока"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("materials:lesson-detail", kwargs={"pk": self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Lesson")

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Updated Lesson",
            "description": "Updated Description",
            "video_url": "https://www.youtube.com/watch?v=updated",
        }
        response = self.client.patch(
            reverse("materials:lesson-update", kwargs={"pk": self.lesson.id}), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Updated Lesson")

    def test_lesson_update_not_owner(self):
        """Тест обновления урока не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        data = {"name": "Updated Lesson"}
        response = self.client.patch(
            reverse("materials:lesson-update", kwargs={"pk": self.lesson.id}), data
        )
        # get_queryset() фильтрует уроки по владельцу, поэтому возвращается 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("materials:lesson-delete", kwargs={"pk": self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_not_owner(self):
        """Тест удаления урока не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(
            reverse("materials:lesson-delete", kwargs={"pk": self.lesson.id})
        )
        # get_queryset() фильтрует уроки по владельцу, поэтому возвращается 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Lesson.objects.count(), 1)


class SubscriptionTestCase(APITestCase):
    """Тесты для функционала подписки на курсы"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание пользователя
        self.user = User.objects.create(email="test@test.com")
        self.user.set_password("test123")
        self.user.save()

        # Создание курса
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )

    def test_subscription_create(self):
        """Тест создания подписки"""
        self.client.force_authenticate(user=self.user)
        data = {"course": self.course.id}
        response = self.client.post(reverse("materials:course-subscribe"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_delete(self):
        """Тест удаления подписки"""
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        data = {"course": self.course.id}
        response = self.client.post(reverse("materials:course-subscribe"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_unauthenticated(self):
        """Тест подписки неаутентифицированным пользователем"""
        data = {"course": self.course.id}
        response = self.client.post(reverse("materials:course-subscribe"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_invalid_course(self):
        """Тест подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user)
        data = {"course": 9999}
        response = self.client.post(reverse("materials:course-subscribe"), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CourseTestCase(APITestCase):
    """Тесты для CRUD операций с курсами"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание пользователей
        self.user = User.objects.create(email="test@test.com")
        self.user.set_password("test123")
        self.user.save()

        self.other_user = User.objects.create(email="other@test.com")
        self.other_user.set_password("test123")
        self.other_user.save()

        # Создание курса
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )

        # Создание урока для курса
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            video_url="https://www.youtube.com/watch?v=test",
            owner=self.user,
        )

    def test_course_list(self):
        """Тест получения списка курсов"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("materials:courses-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_course_list_unauthenticated(self):
        """Тест получения списка курсов неавторизованным пользователем"""
        response = self.client.get(reverse("materials:courses-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_create(self):
        """Тест создания курса"""
        self.client.force_authenticate(user=self.user)
        data = {"name": "New Course", "description": "New Description"}
        response = self.client.post(reverse("materials:courses-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(response.data["name"], "New Course")

    def test_course_retrieve(self):
        """Тест получения курса"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Course")
        self.assertEqual(response.data["lessons_count"], 1)
        self.assertEqual(len(response.data["lessons"]), 1)

    def test_course_update_owner(self):
        """Тест обновления курса владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Course", "description": "Updated Description"}
        response = self.client.patch(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id}), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")

    def test_course_update_not_owner(self):
        """Тест обновления курса не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        data = {"name": "Updated Course"}
        response = self.client.patch(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id}), data
        )
        # get_queryset() фильтрует курсы по владельцу, поэтому возвращается 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_delete_owner(self):
        """Тест удаления курса владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    def test_course_delete_not_owner(self):
        """Тест удаления курса не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id})
        )
        # get_queryset() фильтрует курсы по владельцу, поэтому возвращается 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Course.objects.count(), 1)

    def test_course_is_subscribed(self):
        """Тест поля is_subscribed в курсе"""
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])

    def test_course_is_not_subscribed(self):
        """Тест поля is_subscribed когда нет подписки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("materials:courses-detail", kwargs={"pk": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])
