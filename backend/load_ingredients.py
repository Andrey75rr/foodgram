import json
import os
import sys

import django

from recipes.models import Ingredient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


def load_ingredients():
    json_file_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'ingredients.json'
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
                        print(f'Загружено {created} ингредиентов...')

            print(f'Успешно загружено {created} ингредиентов')
            
    except FileNotFoundError:
        print(f'❌ Файл не найден: {json_file_path}')
    except json.JSONDecodeError as e:
        print(f'❌ Ошибка в формате JSON: {e}')

if __name__ == '__main__':
    load_ingredients()