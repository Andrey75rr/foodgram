"""Импорты."""
import random
import string

from django.db import models
from users.models import User


def generate_short_link():
    """Генерирует уникальный короткий код из 6 символов."""
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=6))
        if not Recipe.objects.filter(short_link=code).exists():
            return code


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет в HEX', max_length=7, unique=True)
    slug = models.SlugField('Уникальный слаг', max_length=200, unique=True)

    class Meta:
        """Мета данные."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Строковое представление."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        """Настройки модели Ingredient."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement'
            )
        ]

    def __str__(self):
        """Возвращает строку - название, единица измерения."""
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=100)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        help_text='Загрузите изображение рецепта',
    )
    text = models.TextField(
        'Описание',
        max_length=200,
        blank=True,
        default=''
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    short_link = models.CharField(
        'Короткая ссылка',
        max_length=6,
        unique=True,
        blank=True,
        default=''
    )

    class Meta:
        """Мета данные модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def save(self, *args, **kwargs):
        """Автоматически генерировать короткий код при создании."""
        if not self.short_link:
            self.short_link = generate_short_link()
        super().save(*args, **kwargs)

    def __str__(self):
        """Строковое представление объекта."""
        return self.name


class RecipeIngredient(models.Model):
    """Связующая модель для рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество'
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        """Строковое представление объекта."""
        return f'{self.ingredient.name} - {self.amount}'


class Favorite(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Корзина покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
