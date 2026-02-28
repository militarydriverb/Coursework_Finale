from decimal import Decimal
from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполнение таблицы Payment тестовыми данными'

    def handle(self, *args, **options):
        # Получаем существующие объекты
        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR('Нет пользователей в базе данных'))
            return

        # Создаем тестовые платежи
        payments_data = []

        # Платежи за курсы
        if courses.exists():
            payments_data.extend([
                {
                    'user': users.first(),
                    'course': courses.first(),
                    'amount': Decimal('5000.00'),
                    'payment_method': 'cash'
                },
                {
                    'user': users.first(),
                    'course': courses.first(),
                    'amount': Decimal('7500.50'),
                    'payment_method': 'transfer'
                },
            ])

        # Платежи за уроки
        if lessons.exists():
            payments_data.extend([
                {
                    'user': users.first(),
                    'lesson': lessons.first(),
                    'amount': Decimal('500.00'),
                    'payment_method': 'cash'
                },
                {
                    'user': users.first(),
                    'lesson': lessons.first(),
                    'amount': Decimal('750.00'),
                    'payment_method': 'transfer'
                },
            ])

        # Создаем платежи
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(**payment_data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан платеж: {payment}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Платеж уже существует: {payment}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Всего создано платежей: {Payment.objects.count()}')
        )
