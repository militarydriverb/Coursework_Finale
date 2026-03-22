from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()


@shared_task
def send_course_update_email(course_name, user_email):
    """
    Асинхронная задача для отправки email об обновлении курса.

    Args:
        course_name: Название курса
        user_email: Email пользователя
    """
    subject = f"Обновление курса: {course_name}"
    message = (
        f'Здравствуйте!\n\nКурс "{course_name}", на который вы подписаны, '
        f"был обновлен.\n\nПосетите платформу, чтобы ознакомиться с новыми материалами."
    )
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return f"Email sent to {user_email} about course update: {course_name}"


@shared_task
def block_inactive_users():
    """
    Периодическая задача для блокировки пользователей,
    которые не заходили более месяца.
    """
    # Вычисляем дату месяц назад от текущей даты
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим всех активных пользователей, которые не заходили более месяца
    # Исключаем пользователей без last_login (они еще ни разу не входили)
    inactive_users = User.objects.filter(
        is_active=True, last_login__isnull=False, last_login__lt=one_month_ago
    )

    # Получаем количество пользователей для логирования
    count = inactive_users.count()

    # Блокируем всех найденных пользователей одним запросом
    if count > 0:
        inactive_users.update(is_active=False)
        print(f"Заблокировано {count} неактивных пользователей")
        return f"Заблокировано {count} неактивных пользователей"
    else:
        print("Неактивных пользователей не найдено")
        return "Неактивных пользователей не найдено"
