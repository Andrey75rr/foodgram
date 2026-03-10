import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):
        # Путь к файлу с ингредиентами
        json_file_path = os.path.join(
            settings.BASE_DIR, '..', 'data', 'ingredients.json'
        )
        
        # Очищаем существующие ингредиенты (опционально)
        # Ingredient.objects.all().delete()
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Счетчик для статистики
                created = 0
                
                for item in data:
                    name = item.get('name')
                    unit = item.get('measurement_unit')
                    
                    if name and unit:
                        # Создаем ингредиент
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