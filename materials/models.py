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

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name
