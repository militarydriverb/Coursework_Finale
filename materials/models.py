from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Курс", help_text="Укажите название курса"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Укажите описание курса",
    )
    preview = models.ImageField(
        upload_to="materials/course/preview",
        blank=True,
        null=True,
        verbose_name="Картинка",
        help_text="Загрузите картинку курса",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите владельца курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Урок", help_text="Укажите название урока"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Укажите описание урока",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Курс",
        help_text="Выберите курс",
    )
    preview = models.ImageField(
        upload_to="materials/lesson/preview",
        blank=True,
        null=True,
        verbose_name="Картинка",
        help_text="Загрузите картинку урока",
    )
    video_url = models.URLField(verbose_name="ссылка на видео", blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите владельца урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name='Курс')

    def __str__(self):
        return f"{self.user} - {self.course}"

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
