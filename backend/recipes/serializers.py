"""Импорты."""
from rest_framework import serializers

from users.models import User

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета данные."""

        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор Теги."""

    class Meta:
        """Мета данные."""

        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиенты."""

    class Meta:
        """Мета данные."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Мета данные."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепты."""

    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredient_amounts',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart', 'pub_date'
        )

    def get_is_favorited(self, obj):
        """Любимый рецепт."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Корзина покупок."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Минимальное представление рецепта."""

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
