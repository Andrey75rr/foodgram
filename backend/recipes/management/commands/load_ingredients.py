"""Импорты."""
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка ингредиентов из JSON файла."""

    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):
        """Выполнить команду."""
        json_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.json'
        )

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                created = 0

                for item in data:
                    name = item.get('name')
                    unit = item.get('measurement_unit')

                    if name and unit:
                        Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=unit
                        )
                        created += 1

                        if created % 100 == 0:
                            self.stdout.write(
                                f'Загружено {created} ингредиентов...'
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {created} ингредиентов'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {json_file_path}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка в формате JSON: {e}')
            )
