"""Команда загрузки тегов."""
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Загрузка тегов."""

    help = 'Загрузка тегов'

    def handle(self, *args, **options):
        """Выполнить команду."""
        tags = [
            {'name': 'Завтрак', 'color': '#FF0000', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#00FF00', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#0000FF', 'slug': 'dinner'},
        ]
        Tag.objects.all().delete()
        for tag in tags:
            Tag.objects.create(**tag)
        self.stdout.write(self.style.SUCCESS('Теги загружены'))
