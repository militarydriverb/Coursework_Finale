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
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1500,
        verbose_name="Цена",
        help_text="Укажите цену курса",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите владельца курса",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
        help_text="Дата последнего обновления курса",
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
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
        help_text="Дата последнего обновления урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    course = models.ForeignKey("Course", on_delete=models.CASCADE, verbose_name="Курс")

    def __str__(self):
        return f"{self.user} - {self.course}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("completed", "Завершен"),
        ("failed", "Не удался"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, который оплачивает курс",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        verbose_name="Курс",
        help_text="Курс, который оплачивается",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма", help_text="Сумма платежа"
    )
    stripe_product_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="ID продукта Stripe",
        help_text="Идентификатор продукта в Stripe",
    )
    stripe_price_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="ID цены Stripe",
        help_text="Идентификатор цены в Stripe",
    )
    stripe_session_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="ID сессии Stripe",
        help_text="Идентификатор сессии оплаты в Stripe",
    )
    payment_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Ссылка на страницу оплаты в Stripe",
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
        help_text="Статус платежа",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.user} - {self.course} - {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]
