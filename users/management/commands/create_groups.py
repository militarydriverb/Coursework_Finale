from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает группу модераторов"

    def handle(self, *args, **options):
        group_name = "Модераторы"
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Группа "{group_name}" успешно создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Группа "{group_name}" уже существует')
            )
