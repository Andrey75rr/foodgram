"""Админка рецептов."""
from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн ингредиентов внутри рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        """Число добавлений рецепта в избранное."""
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""

    list_display = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка корзины покупок."""

    list_display = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')
